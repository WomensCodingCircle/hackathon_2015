from django.shortcuts import render
from django.utils import timezone
from django.template import RequestContext

# imports
import httplib
import json
import os
from glob import glob
from pydvid import keyvalue as kv
from pydvid import general
import numpy

server = "emrecon100.janelia.priv"
port = 8000
connection = httplib.HTTPConnection(server, timeout=5.0)

def callDVID(keyname, dataname='emcircuit'):
   uuid = '2a3'
   return kv.get_value(connection, uuid, dataname, keyname)


# def callDVID(keyname, dataname='emcircuit'):
# 	data = ''
# 	if dataname == 'emcircuit':
# 		fi = open(os.path.join('hackathon_app',keyname))
# 		data = fi.read()
# 		fi.close()
# 	elif dataname == 'emcircuitIO':
# 		fi = open(os.path.join('hackathon_app','inputs_outputs.json'))
# 		d = json.load(fi)
# 		fi.close()
# 		data = json.dumps(d[str(keyname)])
# 	return data
	
	
def clothoView(request):
    my_template = 'hackathon_app/user_interface.html'
    neuronList = getNeuronNames()
    combined = None
    types = None
    renderSvg = False
    if request.POST:
        reqVars = dict(request.POST.iterlists())
        comboType = reqVars['combotype']
        neuronSearch = reqVars['neurons[]']
        (combined, types) = processNeuronsRequest(neuronList, neuronSearch, comboType[0])
        renderSvg = True
    data = {
        'neurons' : neuronList,
        'renderSvg' : renderSvg,
        'edges': combined,
        'nodes': types
    }
    return render(request, my_template, data, context_instance=RequestContext(request))


def getNeuronNames():
    data_file = callDVID('names.json')
    NeuronNames = json.loads(data_file)
    NeuronNames.sort()
    return NeuronNames

def processNeuronsRequest(neuronNames, neuronList, comboType):
    list_BodyId = getBodyId(neuronList)
    #for each body id, call getInputsOutputs
    #then call filterInputsOutputs to filter based on neuron list
    allIOs = getInputsOutputs(list_BodyId)
    print allIOs
    filteredIOs = filterInputsOutputs(list_BodyId, allIOs)
    uncombinedOutputs = generateEdgeList(filteredIOs)
    #TODO replace sum with user selection from form
    (combined, types) = combineOutputs(uncombinedOutputs, comboType)
    print "combined", combined
    return combined, types


def getInputsOutputs(neuronIDList):
    #select neurons neuronIDList, puts them in a new dictionary, and return the dictionary to caller
    selected_nodes = {}
    for key in neuronIDList:
	try:
		thisNode = callDVID(int(key), dataname='emcircuitIO')
		thisNode = json.loads(thisNode) 
		selected_nodes[key] = thisNode
	except:
		selected_nodes[key] = {'inputs': {}, 'outputs': {}}
    return selected_nodes

def filterInputsOutputs(neuronIDs, inputsOutputs):
    #remove name
    #remove inputs come from neurons not neuronIDs list
    #remove outputs to neurons not in neuronIDs list
    #returns inputs and outputs that connect to neurons in listOfNeurons

    nodeIDs = inputsOutputs.keys();
    for item in nodeIDs:
        thisNode = inputsOutputs[item]

        #filter input nodes
        thisInputs = thisNode["inputs"]
        thisInputskey = thisInputs.keys()
        for inputNode in thisInputskey:
            if (int(inputNode) in neuronIDs):
                continue
            else:
                del thisInputs[inputNode]
        #filter input nodes
        thisOutputs = thisNode["outputs"]
        thisOutputskey = thisOutputs.keys()
        for outputNode in thisOutputskey:
            if (int(outputNode) in neuronIDs):
                continue
            else:
                del thisOutputs[outputNode]
    return inputsOutputs
	
	
def getBodyId(neuronNames):
    data = callDVID('names_to_body_id.json')
    dic = json.loads(data)
    if neuronNames :
        ## Look up Body Id and add to the list
        lst = []
        for name in neuronNames:
            lst = lst + list(dic.get(name))
        if lst == []:
            return None
        nameSet = set(lst) # Remove duplicated id
        Newlst = list(nameSet)
        return Newlst
    else:
        return None


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
    #new combinedOutputs for returning to caller (UI)
    combinedOutputs = {}
    #keys of input edgeList, in this list every element is unique, eg [("50809", "22077"), ("50809", "16699")]
    idTupleList = edgeList.keys()
    #paraell array for Neuron Type Tuples, in this list elements are not unique eg [('TM3', 'LD5'), ('TM3', 'LD5')]
    typeTupleList = []
    bodyIdToType = json.loads(callDVID('body_id_to_type.json'))
    for idTuple in idTupleList:
        #convert ID tuple to Type tuple
        typeTuple = ( idToType(idTuple[0], bodyIdToType), idToType(idTuple[1], bodyIdToType))
        #add typeTuple to typeTupleList
        typeTupleList.append(typeTuple)
    #combine output by cell type
    #build dictionary key=typeTuple, value = [strengths]
    for index, item in enumerate(typeTupleList):
        strength = edgeList[idTupleList[index]]["strength"]
        if item in combinedOutputs:
            strength = edgeList[idTupleList[index]]["strength"]
            combinedOutputs[item].append(strength)
        else:
            #add an entry to combinedOutputs:  key=typeTuple, object = list of one strength
            combinedOutputs[item] = [strength]
    #now we have a new dictionary
    # key: cell type tuple,  value: strengths for this cell tuple in a list
    # do math to combine strengths
    types = set()
    for item in combinedOutputs.keys():
        types.add(item[0])
        types.add(item[1])
        stregthList = combinedOutputs[item]
        strengthCombined = doMath(stregthList, combinationType)
        if strengthCombined:
            combinedDict = {"destination":item[0], "source":item[1], "strength":strengthCombined}
            combinedOutputs[item] = combinedDict
        else:
            del combinedOutputs[item]
        if (item[0] == item[1]):
            del combinedOutputs[item]

    types = list(types)
    for item in combinedOutputs.keys():
        combinedOutputs[item]['destination'] = types.index(combinedOutputs[item]['destination'])
        combinedOutputs[item]['source'] = types.index(combinedOutputs[item]['source'])

    return combinedOutputs, types


def doMath(integerList, operator):
    #combine Strength of multiple egdes
    #input integer list,  operator
    #return integer
    #Ying Wu
    operators = ['sum', 'max', 'mean', 'average']
    if len(integerList) == 1:
        return integerList[0]
    #sum
    if(operator == 'sum'):
        return numpy.sum(integerList)
    #max
    elif(operator == 'max'):
        return numpy.max(integerList)
    #mean
    elif(operator == 'mean'):
        return numpy.mean(integerList).round()
    #average
    elif(operator == 'median'):
        return numpy.median(integerList).round()
    else:
        print operator

def idToType(id, typeDict):
        id = str(id)
	if id in typeDict:
		return typeDict[id]
	return id

