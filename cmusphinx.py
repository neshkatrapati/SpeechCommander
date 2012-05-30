#!/usr/bin/env python

# Copyright (c) 2008 Carnegie Mellon University,
# Ganesh Katrapati <neshmailsu@gmail.com> 2012
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system.  See
# http://cmusphinx.sourceforge.net/html/LICENSE for more information.

import pygtk
pygtk.require('2.0')
import gtk

import re
import os
import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst

class DemoApp(object):
    """GStreamer/PocketSphinx Demo Application"""
    def __init__(self):
        """Initialize a DemoApp object"""
        self.init_gui()
        self.init_gst()

    def init_gui(self):
        """Initialize the GUI components"""
        self.window = gtk.Window()
        self.window.connect("delete-event", gtk.main_quit)
        self.window.set_default_size(600,200)
        self.window.set_border_width(10)
        vbox = gtk.VBox()
	hb = gtk.HBox()
	
	
	self.speech = gtk.VBox()
	self.speech.pack_start(gtk.Label("History"))	
	hb.pack_start(self.speech)        


	vb = gtk.VBox()
	
	#Getting Commands
	self.get_command_corpus()
	self.result = ""

	data = ""
	
	vb.pack_start(gtk.Label("Available Commands"))	

	for line in self.corpus:
		label = gtk.Label(line)
		vb.pack_start(label)

	hb.pack_start(vb)	

        vbox.pack_start(hb)
	
	self.textbuf = gtk.TextBuffer()
        self.text = gtk.TextView(self.textbuf)
        self.text.set_wrap_mode(gtk.WRAP_WORD)
	
	vbox.pack_start(self.text)	

	self.button = gtk.ToggleButton("Speak")
        self.button.connect('clicked', self.button_clicked)
	   
        vbox.pack_start(self.button, False, False, 5)
     
        self.window.add(vbox)
        self.window.show_all()
	

    def init_gst(self):
        """Initialize the speech components"""
        self.pipeline = gst.parse_launch('gconfaudiosrc ! audioconvert ! audioresample '
                                         + '! vader name=vad auto-threshold=true '
                                         + '! pocketsphinx name=asr ! fakesink')
        asr = self.pipeline.get_by_name('asr')
        asr.set_property('lm', 'corpus.txt.lm')
        asr.set_property('dict', 'corpus.txt.dic')
        asr.connect('partial_result', self.asr_partial_result)
        asr.connect('result', self.asr_result)
        asr.set_property('configured', True)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message::application', self.application_message)

        self.pipeline.set_state(gst.STATE_PAUSED)

    def asr_partial_result(self, asr, text, uttid):
        """Forward partial result signals on the bus to the main thread."""
        struct = gst.Structure('partial_result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def asr_result(self, asr, text, uttid):
        """Forward result signals on the bus to the main thread."""
        struct = gst.Structure('result')
        struct.set_value('hyp', text)
        struct.set_value('uttid', uttid)
        asr.post_message(gst.message_new_application(asr, struct))

    def application_message(self, bus, msg):
        """Receive application messages from the bus."""
        msgtype = msg.structure.get_name()
        if msgtype == 'partial_result':
            self.partial_result(msg.structure['hyp'], msg.structure['uttid'])
        elif msgtype == 'result':
            self.final_result(msg.structure['hyp'], msg.structure['uttid'])
            self.pipeline.set_state(gst.STATE_PAUSED)
            self.button.set_active(False)

    def partial_result(self, hyp, uttid):
        """Delete any previous selection, insert text and select it."""
        # All this stuff appears as one single action
        self.textbuf.begin_user_action()
        self.textbuf.delete_selection(True, self.text.get_editable())
        self.textbuf.insert_at_cursor(hyp)
        ins = self.textbuf.get_insert()
        iter = self.textbuf.get_iter_at_mark(ins)
        iter.backward_chars(len(hyp))
        self.textbuf.move_mark(ins, iter)
        self.textbuf.end_user_action()

    def final_result(self, hyp, uttid):
        """Insert the final result."""
        # All this stuff appears as one single action
	
	self.textbuf.set_text("")
        self.textbuf.begin_user_action()
		
        self.textbuf.delete_selection(True, self.text.get_editable())

        self.textbuf.insert_at_cursor(hyp+"\n")
	btn = gtk.Button(hyp)
	self.speech.pack_start(btn,False,False,5)
	btn.connect("clicked",self.opencmd)
	self.speech.show_all()
	self.result = hyp
        self.textbuf.end_user_action()

    def button_clicked(self, button):
        """Handle button presses."""
        if button.get_active():
            button.set_label("Stop")
            self.pipeline.set_state(gst.STATE_PLAYING)
        else:
            button.set_label("Speak")
            vader = self.pipeline.get_by_name('vad')
            vader.set_property('silent', True)

    def opencmd(self, button):
	os.system(self.corpus[button.get_label()] + " &")
    

	
    def get_command_corpus(self):
	self.corpus = {}
	for line in open("commandcorpus.cr").readlines():
		trueline = line[:-1]
		words = re.split("\s+",line)
		self.corpus[words[0].upper()] = words[1]
	
			

def invoke():
	app = DemoApp()
	gtk.main()
