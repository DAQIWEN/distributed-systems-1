import zmq
from classes.event import *
from classes.heartbeat_client import *
from random import randint
import logging
import json

# assumptions:
# 	only one topic per publisher
# 	
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) #Q will this make it shared between all objects?
hdlr = logging.FileHandler('publisher.log',mode='w')
logger.addHandler(hdlr)

class Publisher:
	# attribiutes
	addr = str(randint(1000,9999))
	# addr = commands.getstatusoutput("ifconfig | awk '/inet addr/{print substr($2,6)}' | sed -n '1p'")[1]
	pId = str(randint(0,999))
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	topic = 'unknown'
    # constructor
	def __init__(self, knownEsAddress, strength ,topic):
		# self.data = []
		self.knownEsAddress = knownEsAddress
		self.socket.connect("tcp://" + self.knownEsAddress)
		self.topic = topic
		self.strength = strength
		self.heartBeatClientObject=heartbeatClient(self.pId,knownEsAddress)



	def register(self,serverAddress):
		# TODO address = lookup(self.topic)
		self.socket.disconnect("tcp://" + self.knownEsAddress)
		self.socket.setsockopt(zmq.RCVTIMEO, 1000)
		#Check before Register
		try:
			self.socket.connect("tcp://" + serverAddress)
			self.heartBeatClientObject.resetAddress(serverAddress)
			self.heartBeatClientObject.start()
			msg = {'msgType':'publisherRegisterReq','pId':self.pId,'address':self.addr, 'topic':self.topic,'os':self.strength}
			self.socket.send_string(json.dumps(msg))
			self.socket.recv()
			# self.socket.send_string("rp{}-{}, {}, {}".format(self.pId, self.addr,self.topic,self.strength))
			logger.info('register request sent')
			return True
		except:
			print ("The node where about to register is dead")
			return False
			#TRY TO RE-LOOKUP
			#NOt Finished

	def lookup(self,key):
		# TODO call to any known eventservice to findout where it should register.
		# return: ES address (ip:port)
		msg = {'msgType':'nodeLookup', 'key': key}
		self.socket.send_string(json.dumps(msg))
		designatedServer = self.socket.recv()
		print('designated server:' , designatedServer)

		#Kevin modified
		while designatedServer == self.knownEsAddress:
			#ask another address
			i=i+1
			msg = {'msgType': 'nodeLookup', 'key': key+i}
			self.socket.send_string(json.dumps(msg))
			self.knownEsAddress = self.socket.recv()

		self.register(designatedServer)
		return designatedServer
		# TODO go register to the designate


	
	def publish(self, event):
		msg = {'msgType':'event','pId':self.pId,'eventDetails': {'topic':event.topic,'body':event.body,'createdAt':event.createdAt}}
		self.socket.send_string(json.dumps(msg))
		self.socket.recv()
		# self.socket.send_string("ev{}-{}".format(self.pId, event.serialize()))
		logger.info('published: ' + event.__str__())
