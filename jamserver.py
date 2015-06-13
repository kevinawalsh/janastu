#!/usr/bin/python

import web
import os
import sys
import hashlib
import time
import re
import subprocess
from os.path import isfile, join, exists

# To do:
# Push event support (partially started)
# Support for annotations, tagging, titles, up/down voting, view statistics, etc.
# Support for searching, sorting, by user name, device name, tag, ranking, most # viewed, etc.
# Better main page: show only most recent, or top-n list, etc.
# Real user accounts, passwords, etc? (prototype uses on-demand user names, no passwords, etc.)
# Use a real database (prototype uses plain text files)
# Thread-safety (prototype is absolutely not thread-safe)
# Support for expiration and deletion of audio clips (clips stay forever in prototype)


#### Settings

# icon_path directory contains .png and other image files, to be used as icons
# in case internet is not reachable, e.g. in hotspot mode for demo, or on a mesh.
icon_path = "./icons"

# known audio format mime-types
icon_formats = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        }

# clip_path directory contains .wav and .mp3 files, each named with a sha224 digest.
clip_path = "./clips"

# templates_path contains html templates for the web site
template_path = "./templates/"
render = web.template.render(template_path)

# clips_file contains info about each clip
clips_file = "clips.txt"

# users_file contains info about each user
users_file = "users.txt"

# known audio format mime-types
audio_formats = {
        "wav": "audio/x-wav", # "audio/vnd.wave",
        "mp3": "audio/mp3",
        }

#default_user_icon = 'http://kodi.tv/wp-content/uploads/DL_Icons_RaspberryPi-new.png'
default_user_icon = '/icon/DL_Icons_RaspberryPi-new.png'

# urls supported by this server
urls = (
    '/', 'index', # Returns nicely-formatted home page, with list of links
    '/listen/(.*)', 'listen', # Returns one audio file
    '/download/(.*)', 'download', # Returns one audio file
    '/icon/(.*)', 'icon', # Returns one icon file
    '/submit', 'submit', # POST; Accepts one audio file for sharing
    '/list', 'listclips', # ?after=date; Returns simple list of audio files
    '/recent/(.*)', 'recent', #  Returns list of audio files more recent than specified digest
    '/test', 'test', # Experimental push support, in progress
    '/events', 'events', # Experimental push support, in progress
)


#### Start of database-like code

# We store information about users and about audio clips. Within python, this
# info is stored in instances of the User and Clip classes. Externally, this is
# stored in plain text files. Actually, they are CSV-formatted files, and we use
# python's csv module to read and write the files. We use a few clever hacks to
# convert between csv file rows and instances of python classes.
import csv

# Info about a single user. Actually, more likely a single Raspberry Pi device.
class User:
    fields = [ 'name', 'icon' ]

    def __init__(self, dictionary):
        for field in User.fields:
            value = dictionary.get(field, None)
            if value is not None:
                value = value.strip()
            setattr(self, field, value)

    def __str__(self):
        return "User " + str(self.__dict__)

# Info about a single audio clip. 
class Clip:
    fields = [ 'digest', 'username', 'rtime', 'stime' ]

    def __init__(self, dictionary):
        self._user = None
        for field in Clip.fields:
            value = dictionary.get(field, None)
            if value is not None:
                value = value.strip()
            setattr(self, field, value)

    def __str__(self):
        return "Clip " + str(self.__dict__)

    def user(self):
        if not self._user:
            user = get_user(self.username)
            if not user:
                user = User({'name': 'Anonymous', 'icon': default_user_icon})
            self._user = user
        return self._user


# Read a csv file and create a list of instances of the given class.
def read_csv(cls, filename):
    lst = []
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, cls.fields)
        for u in reader:
            x = cls(u)
            lst.append(x)
    return lst

# Use a list of instances of the given class to create a csv file.
def write_csv(cls, lst, filename):
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, cls.fields)
        for x in lst:
            dictionary = {}
            for k in cls.fields:
                dictionary[k] = x.__dict__[k]
            writer.writerow(dictionary)

# Global variables to hold the data. This is blatently un-safe for threads.
users = []
clips = []

# Load all user and clip data.
def load():
    global users, clips
    users = read_csv(User, users_file)
    clips = read_csv(Clip, clips_file)

# Save all user and clip data.
def save():
    global users, clips
    write_csv(User, users, users_file)
    write_csv(Clip, clips, clips_file)

# Get User with given name, or None if no such user.
def get_user(name):
    u = [ user for user in users if user.name == name ]
    if u:
        return u[0]
    else:
        return None

# Get Clip with given digest, or None if no such clip.
def get_clip(digest):
    c = [ clip for clip in clips if clip.digest == digest ]
    if c:
        return c[0]
    else:
        return None

#### End of database-like code

# Return main page, showing all clips
class index:
    def GET(self):
        global users, clips
        load()
        return render.index(clips)

# Used for sorting/filtering by date
def after(r, a):
    return time.strptime(r) > time.strptime(a)

# Return list of all clips. Format is a simple list of digests, one per line.
class listclips:
    def GET(self):
        global users, clips
        load()
        i = web.input(after=None)
        items = [ clip.digest for clip in clips if i.after is None or after(clip.rtime, i.after) ]
        #return str(len(items)) + "\n" + "\n".join(items)
        return "\n".join(items)

# Return most recent clips, same format as above. Only those clips that came
# after the specified one are returned.
class recent:
    def GET(self, mostRecentDigest):
        global users, clips
        load()
        i = web.input(after=None)
        items = [ clip.digest for clip in clips if i.after is None or after(clip.rtime, i.after) ]
        if mostRecentDigest in items:
            print "You have up to " + mostRecentDigest
            idx = items.index(mostRecentDigest)
            items = items[idx+1:]
            print "So I will send you " + str(len(items)) + " new things"
        else:
            print "I don't receognize that, so I will send you all " + str(len(items)) + " things"
        return "\n".join(items)

# Return detail page for a single clip.
class listen:
    def GET(self, digest):
        global users, clips
        load()
        digest = digest.split('/')[-1]
        clip = get_clip(digest)
        return render.listen(clip)

# Download a single clip.
class download:
    def GET(self, filename):
        global users, clips
        load()
        filename = filename.lower().split('/')[-1].strip()
        if '.' not in filename:
            raise web.notfound("Sorry, you need to specify the audio file format.")
        digest, ext = filename.split('.', 1)
        clip = get_clip(digest)
        if not clip:
            raise web.notfound("Sorry, no such audio clip.")
        if ext.lower() not in audio_formats:
            raise web.notfound("Sorry, unrecognized audio file format: " + ext)
        path = join(clip_path, clip.digest + "." + ext)
        if not isfile(path):
            raise web.notfound("Sorry, the clip you were looking for is missing.")
        web.header('Content-Type', audio_formats[ext.lower()])
        with open(path) as f:
            return f.read()

# Support for locally-hosted icons.
class icon:
    def GET(self, filename):
        from os import listdir
        from os.path import isfile, join
        filenames = [ f for f in listdir(icon_path) if isfile(join(icon_path,f)) ]
        if filename not in filenames:
            raise web.notfound("Sorry, that icon could not be found.")
        path = join(icon_path, filename)
        name, ext = filename.split('.', 1)
        if ext.lower() in icon_formats:
            web.header('Content-Type', icon_formats[ext.lower()])
        with open(path) as f:
            return f.read()

# Experimental / in progress: push events using yield
class events:
    def GET(self): 
        #web.header("Content-Type", "application/x-dom-event-stream") 
        web.header("Content-Type", "text/event-stream") 
        for i in range(0, 5):
                print "sending an event..."
                #yield "Event: server-time\ndata: %s\n" % time.time() 
                yield "data: %s\r\n\r\n" % time.time() 
                time.sleep(3) 
        return

# Experimental / in progress: push events using yield
class test:
    def GET(Self):
        return """<script>
function eventHandler(event)
{
// Alert time sent by the server
alert(event.data); 
}
var evtSource = new EventSource("events");
evtSource.addEventListener("server-time", eventHandler, false);
evtSource.addEventListener("message", function(e) {
  console.log(e.data);
  console.log("ping");
  }, false);
</script>
Hello, world
<script>
console.log("hello world");
console.log("hello console");
</script>
"""

# Submit an audio clip.
class submit:
    def POST(self):

        print "Got POST"
        i = web.input(date=time.ctime(), username='Anonymous', usericon=None, clip=None)
        i.stime = time.ctime()

        wav = i.clip
        if wav is None or len(wav) == 0:
            raise web.notfound("Sorry, you didn't supply an audio clip!")

        digest = hashlib.sha224(wav).hexdigest()
        print "Got a new clip with length %d, digest is %s" % (len(wav), digest)

        global users, clips
        load()

        # Save user info...
        user = get_user(i.username)
        if not user:
            # Create new user account
            print "Got a new user account " + i.username
            user = User({'name': i.username, 'icon': i.usericon})
            users.append(user)
        elif i.usericon:
            # Update user account
            print "Updating user account " + username
            user.icon = i.usericon

        # Save wav audio data...
        wav_path=join(clip_path, digest + ".wav")
        if isfile(wav_path):
            print "Already have this wav clip, no need to save..."
        elif exists(wav_path):
            raise web.internalerror("Ooops, already have a folder with that name.")
        else:
            print "Saving wav audio..."
            with open(wav_path, 'w') as f:
                f.write(wav)

        # Save mp3 audio data...
        mp3_path=join(clip_path, digest + ".mp3")
        if isfile(mp3_path):
            print "Already have this mp3 clip, no need to save..."
        elif exists(mp3_path):
            raise web.internalerror("Ooops, already have a folder with that name.")
        else:
            print "Converting to mp3..."
            r = subprocess.call(["lame", "-V0", "-h", "-b", "160", "--vbr-new", wav_path, mp3_path])
            if r != 0:
                raise web.internalerror("Can't conver to mp3")

        # Save clip info...
        clip = get_clip(digest)
        if not clip:
            print "Got a new clip " + digest
            clip = Clip({'digest': digest,
                'username': i.username,
                'rtime': i.date,
                'stime': i.stime})
            clips.append(clip)
        else:
            print "Updating clip " + digest
            clip.stime = i.stime
            clip.username = i.username
            clips.remove(clip)
            clips.append(clip)

        # todo, sort by recording time, not submission time?
        save()

        return "OK"


# Main init code
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
