#debug flag. In production set debug="False"
debug = False
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

def callDVID(keyname):
    server = "hackathon.janelia.org"
    uuid = '2a3'
    dataname = 'codingcircle'
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
	
	neuronList = ["Tm3", "L1"]
	
	#request contains neuron names and ids
	print "Neuron names:", getNeuronNames(), 
	
	#generate list of body ids user is interested in (use getBodyIds)
	list_BodyId = getBodyId(neuronList)
	print "Neuron IDs:", list_BodyId 
	
	#for each body id, call getInputsOutputs
	#then call filterInputsOutputs to filter based on neuron list
	
	for list_ID in list_BodyID:
	    
	    print "ID list:", getInputsOutputs(list_ID)
	    
	    print filterInputsOutputs(neuronList, list_ID)
	
	
	#generateEdgeList()
	
	print generateEdgeList()
	
	
	#combineOutputs() based on what type of combination the user wants
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
	pass
	#uses filterInputsOutputs and getBodyIds to generate a list of
    #connections for svg
	#returns list of connections for svg
    #key is the Id of the neuron of interest
            
        for key,value in listOfNeurons.items():
                
            #print key,value
            node = listOfNeurons.get(key)
                
            #getting data from inputs dictionary
            inputs = node.get("inputs")
                
            inconnections = [key, inputs]
                
            #getting data from outputs dictionary
            outputs = node.get("outputs")
                
            outconnections = [key, outputs]
            
        return inconnections
        return outconnections

def combineOutputs(nodes, celltypes, edges, combinationType):
	pass
	#combines nodes by cell type and calculates inputs and outputs base on combo type (mean, sum, etc.)
	#returns nodes, edges 

#test
if debug == True:
    selectedNodes = {}
    try:
        selectedNodes = getInputsOutputs(neuronIDList)
    except:
        print "Unexpected error:", sys.exc_info()[0]

    trimmedInputsOutputs = filterInputsOutputs(neuronIDList, selectedNodes)

    print trimmedInputsOutputs	

