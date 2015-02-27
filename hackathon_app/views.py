#debug flag. In production set debug="False"
debug = True
if debug == False:
    from django.shortcuts import render
    from django.utils import timezone
    from django.template import RequestContext

# imports
import httplib
import json
from os import path
from glob import glob
from pydvid import keyvalue as kv
from pydvid import general

def callDVID(keyname, dataname='codingcircle'):
    server = "hackathon.janelia.org"
    uuid = '2a3'
    connection = httplib.HTTPConnection(server, timeout=30.0)
    keys = kv.get_keys(connection, uuid, dataname)
    if keyname not in keys:
        print "Invalid key", keyname
        return None
    return kv.get_value(connection, uuid, dataname, keyname)

def simple_view(request):
    today = "test"
    data_dictionary = {'today': today}
    my_template = 'hackathon_app/user_interface.html'
    my_data = getNeuronNames()
    return render(request,my_template,{'today':today,'data':my_data,},context_instance=RequestContext(request))

def charlottes_view(request):
    my_template = 'hackathon_app/svg.html'
    return render(request, my_template, context_instance=RequestContext(request))

def getNeuronNames():
    data_file = callDVID('names.json')
    NeuronNames = json.loads(data_file)
    NeuronNames.sort()
    return NeuronNames

def processNeuronsRequest(request):
	#test function
	#test=getInputsOutputs("16699")
	#return test
	
	neuronList = ["Dm3", "C3", "Dm8", "Tm5a-B-ant"]
	
	#request contains neuron names and ids
	print "Neuron names:", getNeuronNames(), 
	
	#generate list of body ids user is interested in (use getBodyIds)
	
	list_BodyId = getBodyId(neuronList)
	print "Neuron IDs:", list_BodyId 
	
	#for each body id, call getInputsOutputs
	#then call filterInputsOutputs to filter based on neuron list
	
	getInOut = getInputsOutputs(list_BodyId)
	print "ID list:", getInputsOutputs(list_BodyId)
	
	print "Neuron Inputs-Outputs:", filterInputsOutputs(neuronList, getInOut)
	
	#generateEdgeList()
	
	print "connections:", generateEdgeList(connections)
	
	#combineOutputs() based on what type of combination the user wants
	print "edge list, operator types:", combineOutputs(edges, combotypes)
	
	#return json data for svg creation
	
	
#sample node list
if debug == True:
    neuronIDList = ["16699", "18631", "22077", "31699", "50809"]

def getInputsOutputs(neuronIDList):
    inputs_outputs = callDVID('inputs_output.json')
    in_out_dict = json.loads(inputs_outputs)

    #select neurons neuronIDList, puts them in a new dictionary, and return the dictionary to caller
    selected_nodes = {}
    for key in neuronIDList:
        thisNode = in_out_dict.get(key)
        selected_nodes[key] = thisNode

    return selected_nodes

def filterInputsOutputs(neuronIDs, inputsOutputs):
    #remove name
    #remove inputs come from neurons not neuronIDs list
    #remove outputs to neurons not in neuronIDs list
    #returns inputs and outputs that connect to neurons in listOfNeurons

    nodeIDs = inputsOutputs.keys();
    for item in nodeIDs:
        thisNode = inputsOutputs.get(item)

        #filter input nodes
        thisInputs = thisNode.get("inputs")
        thisInputskey = thisInputs.keys()
        if debug == True:
            print  item + ": Inputs all " + str(len(thisInputskey))
            for inputNode in thisInputskey:
                if (inputNode in neuronIDs):
                    continue
                else:
                    del thisInputs[inputNode]
        if debug == True:
            print  item + ": Inputs after filter " + str(len(thisInputs.keys()))

         #filter input nodes
        thisOutputs = thisNode.get("outputs")
        thisOutputskey = thisOutputs.keys()
        if debug == True:
            print  item + ": Outputs all " + str(len(thisOutputskey))
            for outputNode in thisOutputskey:
                if (outputNode in neuronIDs):
                    continue
                else:
                    del thisOutputs[outputNode]
        if debug == True:
            print  item + ": Outputs after filter " + str(len(thisOutputs.keys()))

        #delete name
        del thisNode["name"]

    return inputsOutputs
	
	
def getBodyId(neuronNames):
    print neuronNames
    data = callDVID('names_to_body_id.json')
    dic = json.loads(data)
    if neuronNames :
        ## Look up Body Id and add to the list
        lst = []
        for name in neuronNames:
            lst = lst + list(dic.get(name))
            #print lst
        if lst == []:
            return None

        nameSet = set(lst) # Remove duplicated id
        Newlst = list(nameSet)

        #print Newlst
        return Newlst

    else:
        return None
        #print 'None'


def generateEdgeList(listOfNeurons):
    #lei-ann
    #uses filterInputsOutputs to generate a list of connections for svg
    #per Charlott:  only use inputs edges in each node to avoid double counting
    #returns list of connections for svg

    #return a dict object consists of data structure
    #key = (thisNodeID-on-input-List, anotherNodeID-has-input-to-thisNode)#valuse{"destination": thisNodeID-on-input-List, "source": anotherNodeID-has-input-to-thisNode, "strength": inputStrength}

    inconnections = {}

    nodeIDs = listOfNeurons.keys()

    for nodeId in nodeIDs:
        node = listOfNeurons.get(nodeId)
        inputs = node.get("inputs")

        inputKeys = inputs.keys()

        for inputKey in inputKeys:

            strength = inputs.get(inputKey)
            if (strength > 0):
                idTuple = (nodeId, inputKey)
                edgeData = {"destination": nodeId, "source": inputKey, "strength": strength}
                inconnections[idTuple] = edgeData


    return inconnections

def combineOutputs(edgeList, combinationType):
	#combines nodes by cell type and calculates inputs and outputs base on combo type (mean, sum, etc.)
	#returns nodes, edges 
    #Ying Wu
    #new combinedOutouts for returning to caller (UI)
    combinedOutputs = {}

    #keys of input edgeList, in this list every element is unique, eg [("50809", "22077"), ("50809", "16699")]
    idTupleList = edgeList.keys()

    #paraell array for Neuron Type Tuples, in this list elements are not unique eg [('TM3', 'LD5'), ('TM3', 'LD5')]
    typeTupleList = []
    neuronsinfoJson = callDVID('neuronsinfo.json', 'graphdata')

    for idTuple in idTupleList:
        #convert ID tuple to Type tuple
        typeTuple = neuronID2NeuronType(idTuple, neuronsinfoJson)
        #add typeTuple to typeTupleList
        typeTupleList.append(typeTuple)



    #combine output by cell type
    #build dictionary key=typeTuple, value = [strengths]
    for index, item in enumerate(typeTupleList):
        strength = edgeList.get(idTupleList[index]).get("strength")
        if item in combinedOutputs.keys():
            strength = edgeList.get(idTupleList[index]).get("strength")
            combinedOutputs.get(item).append(strength)
        else:
            #add an entry to combinedOutputs:  key=typeTuple, object = list of one strength
            combinedOutputs[item] = [strength]

    #now we have a new dictionary
    # key: cell type tuple,  value: strengths for this cell tuple in a list

    if(debug):
        print "before combine strength"
        print combinedOutputs

    # do math to combine strengths

    for item in combinedOutputs.keys():
        stregthList = combinedOutputs.get(item)
        strengthCombined = doMath(stregthList, combinationType)
        combinedDict = {"destination":item[0], "source":item[1], "strength":strengthCombined}
        combinedOutputs[item] = combinedDict

    if(debug):
        print "after combine strength"
        print combinedOutputs

    return combinedOutputs


def doMath(integerList, operator):
    #combine Strength of multiple egdes
    #input integer list,  operator
    #return integer
    #Ying Wu
    operators = ['sum', 'max', 'mean', 'average']
    if len(integerList) == 1:
        return integerList[0]

    #sum
    if(operator == operators[0]):
        return numpy.sum(integerList)

    #max
    if(operator == operators[1]):
        return numpy.max(integerList)

    #mean
    if(operator == operators[2]):
        return numpy.mean(integerList).round()

    #average
    if(operator == operators[3]):
        return numpy.average(integerList).round()

def neuronID2NeuronType (idTuple, neuronsinfoJson):
    #Ying Wu
    targetID = idTuple[0]
    targetType = getNeuronType(targetID, neuronsinfoJson)
    sourceID = idTuple[1]
    sourceType = getNeuronType(sourceID, neuronsinfoJson)
    return (targetType, sourceType)



