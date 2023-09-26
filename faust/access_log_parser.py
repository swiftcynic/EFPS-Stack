import json
import httpagentparser
import faker
# Can use below to get countries but very costly:
# from ip2geotools.databases.noncommercial import DbIpCity

from numpy.random import choice
from apachelogs import LogParser

class AccessLogParser:
	def __init__(self):
		log_format = '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'
		self.log_parser = LogParser(log_format)
		self.fake = faker.Faker()
	
	def parse(self, event):
		
		output = self.log_parser.parse(event)
		
		row = {
			**output.headers_in,
			**output.directives
		}
		
		method, url, protocol = row['%r'].split()
		row['method'] = method
		row['url'] = url
		row['protocol'] = protocol
		
		agent_parts = httpagentparser.detect(row['User-Agent'])
		for k, v in agent_parts.items():
			row[k] = v
			
		FIELDS_TO_DROP = ['%r', '%l', '%{Referer}i', '%{User-Agent}i']
		for field in FIELDS_TO_DROP:
			del row[field]
			
		OLD_NEW = {
			'%>s': 'status',
			'%h' : 'hostName',
			'%b': 'responseBytes',
			'%t': 'ts',
			'%u': 'uid',
			'Referer': 'referer',
		}
		
		for oldField, newField in OLD_NEW.items():
				row[newField] = row.pop(oldField)
		
		row['ts'] = str(row['ts'].strftime('%Y-%m-%d %H:%M:%S'))
		row['bot'] = bool(choice([1, 0], p=[0.051, 0.949]))
		row['country'] = self.fake.country_code() #DbIpCity.get(row['hostName'], api_key='free')
		return(row)

#####
if __name__ == '__main__':
	import time
	parser = AccessLogParser()
	event = '105.201.240.203 - Kari [01/Mar/1970:00:30:42 +0530] "DELETE /wp-admin HTTP/1.1" 257 5053 "https://downs.com/terms/" "Mozilla/5.0 (Windows NT 4.0; bem-ZM; rv:1.9.2.20) Gecko/4269-06-27 03:45:02 Firefox/4.0"'
	print(parser.parse(event))
	start = time.time()
	for _ in range(16000):
		parser.parse(event)
	end = time.time()
	print("The time of execution of above program is :", (end-start) * 10**3, "ms")
	
####