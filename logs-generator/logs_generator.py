# Importing Required Library
import time
import datetime
import random
import argparse
import os

import numpy as np

from faker import Faker
from random import randrange
from tzlocal import get_localzone

# Argument Parsing
parser = argparse.ArgumentParser(__file__, description='Fake Apache Log Generator')

parser.add_argument('--output', '-o',
                    dest='output_type',
                    help='Write to a Log file or to STDOUT',
                    choices=['LOG','CONSOLE'],
                    default='CONSOLE')

parser.add_argument('--mode', '-m',
                    dest='mode',
                    help='Mode of log generation DDOS attack or healthy',
                    choices=['ddos','healthy'],
                    default='healthy')

parser.add_argument('--num', '-n',
                    dest='num_lines',
                    help='Number of lines to generate (0 for infinite)',
                    type=int,
                    default=0)

parser.add_argument('--sleep', '-s',
                    help='Sleep this long between lines (in seconds)',
                    type=float,
                    default=0.0)

args = parser.parse_args()

num_lines = args.num_lines
output_type = args.output_type
mode = args.mode

# Faker object to fake: ip, userID, userAgents, referer
faker = Faker()

# Followed time format through out
time_format = "%d/%b/%Y:%H:%M:%S"
time_zone = get_localzone()

# reading the time of generating responses
up_time = datetime.datetime.now()
try:
    with open('latest_time.txt', 'r') as file:
        time_in_file = file.readline()
        up_time = datetime.datetime.strptime(time_in_file, time_format)
except FileNotFoundError:
    pass
except ValueError:
    raise ValueError(f"time data '{time_in_file}' does not match format '%d/%b/%Y:%H:%M:%S'")
    
responses_list=[200,400,500,300]
response_probability = [0.96, 0.0036, 0.025, 0.0114] if mode=='healthy' else [0.3,0.41,0.21,0.08]

verbs_list = ["GET","POST","DELETE","PUT"]
verbs_probability = [0.6,0.1,0.1,0.2]

resources_list = ["/list","/wp-content","/wp-admin","/explore","/search/tag/list","/app/main/posts","/posts/posts/explore","/apps/cart.jsp?appID="]

ua_list = [faker.firefox, faker.chrome, faker.safari, faker.internet_explorer, faker.opera]
ua_probability = [0.3,0.35,0.1,0.2,0.05]

if not os.path.exists('../logs-data/'):
    os.makedirs('../logs-data/')

flag = True
while flag:
    
    if args.sleep:
        increment = datetime.timedelta(seconds=args.sleep)
    elif up_time.strftime('%Y/%m/%d')<datetime.datetime.now().strftime('%Y/%m/%d'):
        increment = datetime.timedelta(seconds=random.randint(30, 300))
    else:
        increment = datetime.timedelta(microseconds=random.randint(200,1000))
        
    up_time += increment
    
    ip = faker.ipv4()
    
    id = '-'
    
    uid = faker.first_name()
    
    dt = up_time.strftime(time_format)
    with open('latest_time.txt', 'w') as time_file: time_file.write(dt)
    
    tz = datetime.datetime.now(time_zone).strftime('%z')
    
    vrb = np.random.choice(verbs_list, p=verbs_probability)
    
    url = random.choice(resources_list)
    if url.find("apps")>0:
        url += str(random.randint(1000,10000))
        
    resp = np.random.choice(responses_list,p=response_probability)
    resp = resp+random.randint(0, 99)
    
    byt = int(random.gauss(5000,50))
    
    referer = faker.uri()
    
    useragent = np.random.choice(ua_list, p=ua_probability)()
    
    log = f'{ip} {id} {uid} [{dt} {tz}] \"{vrb} {url} HTTP/1.1\" {resp} {byt} \"{referer}\" \"{useragent}\"\n'
    
    if output_type == 'LOG':
        uptime_year_month = up_time.strftime('%Y_%m')
        with open(f'../logs-data/logs_{uptime_year_month}.log', 'a+') as out_file:
            out_file.write(log)
    elif output_type == 'CONSOLE':
        print(log, end='')
        
    num_lines -= 1
    flag = True if num_lines else False