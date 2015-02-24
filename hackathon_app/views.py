# from django.shortcuts import render
#from django.utils import timezone
#from django.template import RequestContext

# imports
import httplib
import json
from os import path
from glob import glob
from pydvid import keyvalue as kv
from pydvid import general

#connect
server = "hackathon.janelia.org"
uuid = '2a3'
dataname = 'codingcircle'

def simple_view(request):
	today = timezone.now()
	data_dictionary = {'today': today}
	my_template = 'hackathon_app/user_interface.html'
	return render(request,my_template,{'today':today},context_instance=RequestContext(request))

def getNeuronNames():

	# Open a connection to DVID
	connection = httplib.HTTPConnection(server, timeout=5.0)

	#get the names of files
	keys = kv.get_keys(connection, uuid, dataname)

	#read file 'names.jason'
	data_file = kv.get_value(connection, uuid, dataname, 'names.json')
	NeuronNames = json.loads(data_file)
	return NeuronNames
	
def processNeuronsRequest(request):
	pass
	#request contains neuron names and ids
	#generate list of body ids user is interested in (use getBodyIds)
	#for each body id, call getInputsOutputs
	#then call filterInputsOutputs to filter based on neuron list
	#generateEdgeList()
	#combineOutputs() based on what type of combination the user wants
	#return json data for svg creation
	
def getInputsOutputs(neuronID):
	pass
	#ying
	#contacts DVID
	#returns all inputs and outputs from one neuron
	
def getBodyIds(neuron, typeName):
	pass
	#satako
	#contacts dvid
	#returns list of ids corresponding to neuron or type name

def filterInputsOutputs(listOfNeurons, inputsOutputs):
	pass
	#ying
	#returns inputs and outputs that connect to neurons in listOfNeurons
	
def generateEdgeList(listOfNeurons):
	pass
	#lei-ann
	#uses filterInputsOutputs and getBodyIds to generate a list of connections for svg
	#returns list of connections for svg

def combineOutputs(nodes, celltypes, edges, combinationType):
	pass
	#combines nodes by cell type and calculates inputs and outputs base on combo type (mean, sum, etc.)
	#returns nodes, edges 

 
	

