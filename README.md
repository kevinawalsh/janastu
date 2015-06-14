Janastu Jam Social Audio Prototype
==================================

This project contains code for a prototype "social audio" app written by Kevin
Walsh, David Mulry, and Rahul Malik over a very short (too short -- just a few
days!) internship at [Janastu](http://janastu.org/), near the end of a one-month
[May-mester study tour](http://hcbengaluru.tumblr.com) in Bangalore, India,
sponsored by the [College of the Holy Cross](http://holycross.edu/).

More details about the intent of the prototype and the great time we had at
Janastu will be coming soon!

Background
----------

During May and June 2015, students from College of the Holy Cross, Worcester
Massachusetts, traveled to Bangalore India for a *Social Justice in Context*
may-mester study program. We chose Bangalore, the "IT capital of India",
specifically because many of us at Holy Cross are interested in technology, and
we wanted to see how technology and the IT industry are impacting Indian
society. Mat Schmalz, professor of religious studies, and Kevin Walsh from the
department of mathmatics and computer science, led the trip. Eight students
participated, drawn from diverse backgrounds including computer science,
religious studies, women's and gender issues, and political science.

On 23 May 2015, many of the folks from Janastu and Hackergram met with our
entire group for an afternoon. We got a great overview of some of the projects,
Arvind gave a nice demo of one of the annotation projects, and we spent a lot of
time discussing social issues. Rahul, David, and Kevin then spent two days at
"the farm" in Devarayana Durga hills. There, Arjun, Deepta, Bhanu, Abhi, and
many others helped us gain a much deeper sense of the work being done in the DD
hills on mesh networking, and Bhanu talked with us about annotation.

Over the next few days, our small team spent some time in a mini-internship at
Janastu's Bangalore office, where have been putting together a small prototype
"social audio app", for possible future deployment on the mesh network at DD
hills and on the web. 

On Sunday, 14 June 2015, the folks from Janastu, Hackergram, and many friends
will hold a short presentation and demo about the work we have done so far, and
how it might be extended or evolve to include more social aspects, like
annotations, ranking and voting, searching, etc. 

Concept: Audio Social Interaction with a Mesh-Connected Raspberry Pi
====================================================================

The system is meant to be a low-cost and simple way for all people -- whether
literate or not -- to record and share audio clips with friends, their
communities, and the world. Use cases might include trivia-like games,
question-and-answer forums, translation services, voice-messaging, open
governance, and so on. 

Hardware
--------

The basic scenario involves distributing low-cost [Raspberry
Pi](https://www.raspberrypi.org/) devices to individual homes in rural
community. Each Pi is equipped with a wireless network adapter, so it can
communicate over a wireless mesh network with other Pi devices and with
locally-connected servers at Janastu's Devarayana Hills Hackergram collective.
Internet access is not yet available, but may be in future. The wireless mesh is
already being deployed, and this app is one of the first designed specifically
for deployment on this mesh.

For this app, each Pi needs the ability to record and playback audio, and it has
some user interface. Each Pi can be connected over HDMI to a television (which
are common in the area), or a separate screen, and can accept a mouse, keyboard,
speakers, microphone, etc. Alternatively, the Pi can operate in screenless mode,
without any screen or keyboard, using alternative forms of input and output like
buttons, LEDs, and audio inpput/output. For our demo, we purchased on short
notice low-cost widely-available web cams from local shops in Bangalore. This
was used as our audio input. For audio output, we used simple external speakers
or HDMI monitors with built-in speakers.


Software: Jam Social Audio Server
---------------------------------

We used Python and [web.py](http://webpy.org) to quickly build a web server for
hosting and managing audio clips, user data, etc. Using a standard web browser,
users can see a list of clips, show details on individual clips (recording time,
submission time, name of the device on which it was recorded, etc.), and users
can play back the audio. Eventually, social aspects would be supported by the
server, such as tagging audio clips, editing meta-data (title, topics, etc.)
ranking, searching and sorting, and annotating.

The server would be hosted on a central machine connected to the mesh network.

Software: Jam Social Audio Clients
----------------------------------

Client apps allow users to record audio clips, share them to the mesh, and
listen to audio clips shared by others.

We made two separate client apps, one using a keyboard and screen for user
interaction, the other using only a three-button mouse (making use of just the
buttons) with no screen or keyboard. Both apps can run on the Pi devices or on a
standard linux box. The screen version provides a simple interface designed with
low-literacy users in mind. It uses the mouse, but does not require any keyboard
interaction. The screenless version uses only the buttons on a three-button
mouse, and does not require the Pi to be connected to a screen or keyboard at
all.

Use Cases
=========

1. "Press to sing" - Each Pi has a button to record voice clips, singing, etc.
Clips can then be played back by all other pis in the mesh.

2. "Trivia game" - One person can record a question (e.g. a riddle or a song
about an unspecified animal). Other people can listen and respond, original
person can pick a winner, or all people can vote, tag, or comment.

3. "Yahoo Answers / Ask.com" - One person can record a question, other people
can respond with answers.

4. Polling / consensus gathering - Proposals can be made, responses collected by
voice.

Milestones and Status
=====================

1. Basic Pi set up and configuration - done
2. Pi audio/video working using 3rd party software - done
3. Pi can record to file, play back clips using Python - done
4. Record a clip on one device, play on others - done
5. Download queue of clips, play back in turn - done
6. Web interface for viewing and playing clips - done
7. Better queue management options on Pi devices (play again, skip, etc.)
8. Support "conversations" so users can reply to a specific clip
9. Allow voting from Pi devices or track clip popularity
10. Web interface for recording or uploading
11. Web interface for tagging, sorting, searching, and management

