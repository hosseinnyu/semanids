## @package analyzer
#  This package includes analyzer classes
import collections
import time
import bisect
from operator import itemgetter
import logging
import dashboard
import consumer
import sensor

#logging.getLogger().setLevel(logging.INFO)

## @class analyzer
#  This is a superclass that includes abstract methods to setup an analyzer and do analysis on data

class Analyzer:

	## @method initializes the class
	def __init__(self, consumer, fieldname, buffertimelimit):
		self.consumer          = consumer
		self.buffer            = []
		self.buffer_time_limit = buffertimelimit #10*1000 ## in ms 
		self.field_name        = fieldname
		self.timestamps        = []

	## @method this method reads the data from the network consumer 
	def readdata(self):
		return self.consumer.getdata(self.field_name)
	
	## @method this method installs the analyzer on to a dashboard that makes i
	def installondashboard(self, globalid):
		pass

	def getglobalid(self):
		return self.global_id
	
	def plugto(self, consumer):
		self.consumer = consumer

	def getanalysis():
		pass
	
	def __str__(self):
                return ",".join(map(str, self.buffer))

class FrequencyAnalyzer(Analyzer):
	def __init__(self, globalid, fieldname, buffertimelimit):
		Analyzer.__init__(self, globalid, fieldname, buffertimelimit)
		self.installondashboard(globalid)

	# gives the number of elements in the buffer
	def getcount(self):
		return len(self.buffer)
	
	# gives the most frequent item and number of occurances
	def getanalysis(self):
		timestamps, localbuffer = self.readdata()
		if localbuffer == None:
			return None		

		## removing elements that exceed the buffer
		t = time.time()
                loc = bisect.bisect_left(timestamps, t-self.buffer_time_limit)
                logging.info("Removing from buffer " + str(loc))
                localbuffer = localbuffer[loc:]
                timestamps = self.timestamps[loc:]


		s = [_[1] for _ in localbuffer]
		s = collections.Counter(s)
		
		m_value = 0
		m_count = 0
		for _ in s:
			if s[_]>m_count:
				m_count = s[_]
				m_value = _
		return (len(localbuffer), m_value, m_count)		

	def installondashboard(self, globalid):
                dashboard.Dashboard.install(globalid, self)
	
		
if __name__ == "__main__":
	s  = sensor.Sensor()
        hc = consumer.HttpConsumer()
        hc.plugto(s)
	
	fa = FrequencyAnalyzer( "HTTP_URL_FREQUENCY", "hostname", 60)
	fa.plugto(hc)

	hc.start()
	
	
	print fa.getanalysis()
