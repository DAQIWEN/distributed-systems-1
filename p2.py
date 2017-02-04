from classes.publisher import *
from random import randint
import time

#create a publisher and pass in intial configuration
p1 = Publisher('127.0.0.1:5555',0,'b')
p1.register()
# keep publishing
while True:
	body = "body {}".format(randint(0,9))
	e1 = Event(p1.topic,body)
	p1.publish(e1)
	# sleep for 300ms
	time.sleep(2)