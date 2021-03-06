#!/usr/bin/python

##########################################################################
###Below section is for client code
user_agent = "image uploader"
default_message = "Image $current of $total"

import logging
import os
from os.path import abspath, isabs, isdir, isfile, join
import random
import string
import sys
import mimetypes
import urllib2
import httplib
import time
import re
import time
import socket #may not be necessary
##########################################################################


##########################################################################
###Below is code to give each pi a sort of identity
###Used within upload function
with open("settings.txt") as f:
	#reads all the lines of the file
	#first line is address of the server
	#second line is the name of the pi device
	#third line is the link to a url for an icon for that pi
	lines = f.readlines()
	serverip, username, usericon = lines
##########################################################################


##########################################################################
###Below section is for pi recording code
from Tkinter import * #Note Tkinter for python 2.*, tkinter for python 3+
import subprocess
import signal
import os
##########################################################################


##########################################################################
###Below section is for client code
user_agent = "image uploader"
default_message = "Image $current of $total"

import logging
import os
from os.path import abspath, isabs, isdir, isfile, join
import random
import string
import sys
import mimetypes
import urllib2
import httplib
import time
import re
##########################################################################


##########################################################################
###Below is code  for pi recording

recording = False
 
#Set display sizes
WINDOW_W =2001
WINDOW_H =2001

def createDisplay():
	###creates window with buttons and calls other functions accordingly
 	global tk
 	tk = Tk()

 	#Add a canvas area ready for drawing on
 	canvas = Canvas(tk, width=WINDOW_W, height=WINDOW_H, bg='#006600')
 	canvas.pack()
	tk.title('Raspberry Jam')
	canvas.bind('<Button-1>', start_Recording)
	canvas.bind('<ButtonRelease-1>', stop_Recording)
	canvas.bind('<Button-3>', start_Playing)
	canvas.bind('<ButtonRelease-3>', stop_Playing)
	#canvas.bind('<Double-3>', terminate)
	#canvas.bind('<Double-1>', share_Song)
	canvas.bind('<Button-2>', play_Download)
	canvas.bind('<Button-4>', next_Song)
	canvas.bind('<Button-5>', previous_Song)

	
 	# Start the tk main-loop (this updates the tk display)
 	tk.mainloop()

def start_Recording(event):
        print 'Got left mouse button click:' 
	global tk, soundfile, p, pid, recording, shell
	if not recording:
		recording = True
		soundfile = open('Latest.wav', 'w')
		p = subprocess.Popen(["arecord", "-D", "hw:1,0", "-f", "s16_le"], stdout=soundfile, shell=False)
		os.system("echo none >/sys/class/leds/led0/trigger")
		os.system("echo 1 >/sys/class/leds/led0/brightness")

def stop_Recording(event):
	###function to change green LED light and start and stop recording and changes the icon for recording
 	global tk, soundfile, p, pid, recording, shell
	print 'Got left mouse button release:'
	if recording: 	
		# Get the process id
		pid = p.pid
		os.kill(pid, signal.SIGINT)
		recording = False
		os.system("echo none >/sys/class/leds/led0/trigger")
		os.system("echo 0 >/sys/class/leds/led0/brightness")
		if not p.poll():
   			print "Process correctly halted"
		#then have client code sent to http server
		upload("Latest.wav")
		get_list()

def start_Playing(event):
        print 'Got right mouse button click:' 
	###function to operate the play button, first op to select output, second op to play that recording
 	global tk, p
	# 1 at end of next line is for output to headset, 2 is for output to HDMI
	os.system("amixer cset numid=3 1")
	# THis plays the audio file
	p = subprocess.Popen(["aplay", "Latest.wav"], shell=False)

def stop_Playing(event):
	print 'Got right mouse button release click:'
	pid = p.pid
	os.kill(pid, signal.SIGINT)
	



def share_Song(event):
	print 'shared'

def play_Download(event):
	print 'playing downlaoded song'
	###function to operate the play button, first op to select output, second op to play that recording
 	global tk, p
	# 1 at end of next line is for output to headset, 2 is for output to HDMI
	os.system("amixer cset numid=3 1")
	# this plays the audio file
	get_list()
	with open("playlist.txt", 'r') as f:
		digests = f.readlines()
	        f.close()
	if len(digests) > 0:
		print digests
		# THis plays the audio file
		os.system("aplay clips/" + digests[0].strip() + ".wav")
		digests = digests[1:]
		with open("playlist.txt", 'w') as f:
			f.write("".join(digests))
			f.close()

def next_Song(event):
	print 'next song on the list'

def previous_Song(event):
	print 'previous song on the list'

def terminate(event):
	###function to kill the system
 	global tk
 	tk.destroy()
 
def main():
 	createDisplay()

###End of record pi code
##########################################################################

##########################################################################
###Below code is the code for the client

def random_string (length):
   	return ''.join (random.choice (string.letters) for ii in range (length + 1))

def encode_multipart_data (data, files):
   	boundary = random_string (30)

    	def get_content_type (filename):
    		return mimetypes.guess_type (filename)[0] or 'application/octet-stream'

    	def encode_field (field_name):
    		return ('--' + boundary,
    	        	'Content-Disposition: form-data; name="%s"' % field_name,
    	        	'', str (data [field_name]))

    	def encode_file (field_name):
    		filename = files [field_name]
    		return ('--' + boundary,
    	        	'Content-Disposition: form-data; name="%s"; filename="%s"' % (field_name, filename),
    	        	'Content-Type: %s' % get_content_type(filename),
    	        	'', open (filename, 'rb').read ())

    	lines = []
    	for name in data:
    		lines.extend (encode_field (name))
    	for name in files:
    		lines.extend (encode_file (name))
   	lines.extend (('--%s--' % boundary, ''))
   	body = '\r\n'.join (lines)

    	headers = {'content-type': 'multipart/form-data; boundary=' + boundary,
               	'content-length': str (len (body))}

    	return body, headers

def send_post (url, data, files):
    	req = urllib2.Request (url)
    	connection = httplib.HTTPConnection (req.get_host ())
    	connection.request ('POST', req.get_selector (),
                        *encode_multipart_data (data, files))
    	response = connection.getresponse ()
    	print ('response = %s', response.read ())
    	print ('Code: %s %s', response.status, response.reason)
    
def upload(filename):
	#this function uploads the audio files to the server
	#it uses the varibles serverip, username, and usericon taken from each pi's settings.txt file
	#these variables are taken from the file in the beginning of the code
	global serverip, username, usericon
	print "made it to before upload"
    	send_post("http://"+serverip+"/submit", {"date":time.ctime(), "username":username, "usericon":usericon}, {"clip":filename})
	print "made it to after upload"

###End of client code
##########################################################################
    	
##########################################################################
###GET LIST OF AUDIO
# this function sends a get request to the server specified in the settings.txt file
# then receives a list of all the audio file names and splits by lines and saves as digest
# then iterates through the digest calling get_audio to retrieve files


def get_list ():
	if os.path.exists("last.txt"):
		with open("last.txt", 'r') as f:
			last = f.readlines()[0]
			f.close()
	else:
		last = "none"
	if os.path.exists("playlist.txt"):
		with open("playlist.txt", 'r') as f:
			digests = f.readlines()
			f.close()
	else:
		digests = []
	if last == "none":
		#if you haven't downloaded any audio files get them all
		url = "http://"+serverip+"/list"
	else:
		#else request everything after the most recent one you have downloaded
		url = "http://"+serverip+"/recent/" + last
    	req = urllib2.Request (url)
    	connection = httplib.HTTPConnection (req.get_host ())
    	connection.request ('GET', req.get_selector ())
    	response = connection.getresponse ()
    	data = response.read()
	results = data.splitlines()
	print "I got some results!"
	for digest in results:
		print "downloading new" + digest
		#CALL GET_AUDIO HERE
		get_audio("http://"+serverip+"/download/", digest+".wav")
	if len(results) > 0:
		with open("playlist.txt", 'a') as f:
			print "appending " + str(results)
			f.write("\n".join(results) + "\n")
			f.close()
		last = results[-1]
		with open("last.txt", 'w') as f:
			f.write(last + "\n")
			f.close()
	###############
	###this code updates the list every s seconds
	#s = 0
	#while s<=30:
		#print s, "seconds"
		#s += 1
		#time.sleep(1)
		#if s == 30:
			#get_list()
	###############
    	print ('Code: %s %s', response.status, response.reason)

###end of get list
##########################################################################

##########################################################################
###GET AUDIO
# this function takes a specific line of the digest and checks to see if it already exists on the pi
# if so it returns to the get_list for loop
# else it makes a second get request to download that specific audio file
# then creates a file named after it and stores it within and closes it
# then returns to get_list for loop

def get_audio (urlpart, urlending):
	if os.path.exists("clips/"+urlending):
		return
	else: 
	    	req = urllib2.Request (urlpart+urlending)
	    	connection = httplib.HTTPConnection (req.get_host ())
	    	connection.request ('GET', req.get_selector ())
	    	response = connection.getresponse ()
		data = response.read()
		print len(data)
		with open("clips/"+urlending, 'w') as f:
	            f.write(data)
	            f.close()
	    	print ('Code: %s %s', response.status, response.reason)

###end of get audio
##########################################################################


get_list()

if __name__ == '__main__':
 	main()
    
