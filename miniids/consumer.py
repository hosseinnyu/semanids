## @package consumer
#  This package sits on top of the sensor class and extracts and buffers the packets observed on the network interface

import sensor
import logging
import collections
import time
import analyzer
import bisect
from   operator import itemgetter

## @var HTTPPacket is a namestuple construct to make it easy to access fields
HTTPPacket = collections.namedtuple('HTTPPacket', 'hostname, path, method, dport, sport, src, dst, timestamp')

## @class consumer supper class for consumers
#  This calss has buffers that stores the packers
class Consumer(object):
	
	## @method Initializes the class
	#  @var sensor: keeps the reference to the sensor that reads the packets
	#  @var buffer: keeps and array of packets after the interesting fields are extracted
	#  @var buffer_time_limit: defines age in which the packets whould be discarded (in seconds)
	#  @var timestamps: an array that keeps the timestamps of the recieved packets. The major use is to identify old packets
	
	def __init__(self, buffertimelimit):
		self.sensor        = None
                self.buffer        = []
                self.buffer_time_limit   = buffertimelimit
                self.timestamps    = []

	def getdata():
		pass
## @class HttpConsumer
#  This is a subclass of Consumer class, that is able to dismantle the elements of HttpPackets
class HttpConsumer(Consumer):
	
	## Initializes this class and the super class
	def __init__(self, buffertimelimit=10):
		super(HttpConsumer, self).__init__(buffertimelimit)

	## plugs this class to a sensor and subscribes for notifictions as a packet is recieved
	def plugto(self, sensor):
                self.sensor = sensor
		self.sensor.plugin('HTTP', self)
	
	## This method is called by Analyzer class to compile and return the of interest
	#  @param fieldname indicate the field(s) of interests in a packet
	def getdata(self, fieldname):
		self.truncateexpired()
		tempbuffer = []
		for f in self.buffer:
			fields = fieldname if isinstance(fieldname, list) else [fieldname]
			v = ",".join([getattr(f, _) for _ in fields])
			tempbuffer.append((getattr(f, "timestamp"),v))
		return (self.timestamps, tempbuffer)

	## This method processes an incomming packet and shapes it to the named tuples
	def process(self, httppacket):
		return HTTPPacket(httppacket.Host, httppacket.Path, httppacket.Method, httppacket.dport, httppacket.sport, httppacket.src, httppacket.dst, time.time())
	
	## A method that removes the old entries from the buffer.
	#  All entries older than currenttime-buffer_time_limit will be removed
        def truncateexpired(self):
                t = time.time()
                loc = bisect.bisect_left(self.timestamps, t-self.buffer_time_limit)
                logging.info("Removing from buffer " + str(loc))
                self.buffer = self.buffer[loc:]
                self.timestamps = self.timestamps[loc:]
	
	## A method to add entries to the consumers buffer
	def addtobuffer(self, packet):
                logging.info("Adding to buffer")
                p = self.process(packet)
		self.buffer.append(p)
                self.timestamps.append(getattr(p, "timestamp"))
		self.truncateexpired()
	
	## A method which is called by the sensor whenever a new packet is arrived
	def notify(self, httppacket):
		self.addtobuffer(httppacket)
		pass
	
	## starts the sensor
	def start(self):
		self.sensor.start()

if __name__=="__main__":
	s = sensor.Sensor()
	hc = HttpConsumer()
	hc.plugto(s)
	#hc.subscribe()
	#hc.add_analyzer("FREQUENCY", "HTTP_URL_FREQUENCY", "hostname", 10)
	hc.start()
