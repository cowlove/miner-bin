import time
import sys
import os
import calendar
import datetime
import re
from subprocess import Popen, PIPE

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic == "miner/rates":
	    (miner,rate)=msg.payload.split()
	    lograte("MRATE", miner, rate)
    m = re.search('/sonoff_(miner(\d+))/power', msg.topic, re.IGNORECASE)
    if m and re.match('off', msg.payload, re.IGNORECASE):
	logprint("Observed MQTT power-on for " + m.group(1))
	mark_rebooting(m.group(1))

	

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_start()

tmo = 40  
reboot_time = 140 # extra time for a reboot 
fake_report_period = 20   # Fake missing reports with -1 rates
lastSeen = {}
lastSeen["miner2"] = 0
lastSeen["miner1"] = 0
lastSeen["miner3"] = 0
lastSeen["miner4"] = 0
rebooting = {}
fakereports = {}


def logprint(msg):
	print( "%s %d %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), calendar.timegm(time.gmtime()), msg))
	
def lograte(fr, miner, rate):
	now = calendar.timegm(time.gmtime())
	prevLastSeen = lastSeen.get(miner, 0)
	try:
		rate = float(rate)
	except:
		rate = -1;

	logprint("%s %s %.1f (%d/%d)" % (fr, miner, rate, now-prevLastSeen, tmo + rebooting.get(miner, 0)))
	if (rate > 300):
		lastSeen[miner] = now
		rebooting[miner] = 0

def query_miner_ethminer(miner):
	process = Popen(["miner-ethrate", miner], stdout=PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()
	try:
		rate = float(output)*637/25.5
	except:
		rate = -1;
	lograte("HRATE", miner + "-e",rate)
  	
def query_miner_xmrstak(miner):
	process = Popen(["miner-xmrrate", miner], stdout=PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()
	lograte("HRATE", miner,output)

def mark_rebooting(host): 
    now = calendar.timegm(time.gmtime())
    lastSeen[host] = now
    rebooting[host] = reboot_time;

def loop():
	#query_miner_ethminer("miner1");
	for host,t in lastSeen.items():
		now = calendar.timegm(time.gmtime())
		if t == 0:
			t = now
			mark_rebooting(host)
			pass
		# TODO: fix query_miner() can take so long that now is very stale		
		#if (now - t > 20):
		#	query_miner(host) 
		#	pass
		if (now - t > tmo + rebooting[host]):
			logprint("RESET " + host + " XXXXXXXXXXXXXXXXXXXXXX %d-%d > %d" % (now, t, tmo + rebooting[host])		)
 			os.system("miner-reset " + host);
			#os.system("sendemail -f jim3vans@gmail.com -t jim@vheavy.com -u 'RESET "+host+"' -m '\n' -s smtp.gmail.com:587 -o tls=yes -xu jim3vans@gmail.com -xp ratpod53g")
			mark_rebooting(host)		
		
		if (now - t > fake_report_period):
			lograte("FRATE", host, "-1")


while True:
	loop()
	time.sleep(15)

