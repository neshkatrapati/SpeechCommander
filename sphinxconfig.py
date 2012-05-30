#!/usr/bin/env python

# Copyright (c) 2008 Carnegie Mellon University.
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system.  See
# http://cmusphinx.sourceforge.net/html/LICENSE for more information.

import pygtk
pygtk.require('2.0')
import gtk

import re
import os
from updateCorpus import *

import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst

class Settings(object):

    def __init__(self):
        
        self.init_gui()
  

    def init_gui(self):
        """Initialize the GUI components"""
        self.window = gtk.Window()
        self.window.connect("delete-event", gtk.main_quit)
        self.window.set_default_size(400,200)
        self.window.set_border_width(10)
	self.get_command_corpus()
	self.result = ""
	print self.corpus
        vbox = gtk.VBox()  
	self.box = vbox
	self.show_boxes(vbox)
        self.button = gtk.ToggleButton("Save")
        self.button.connect('clicked', self.button_clicked)
	self.obutton = gtk.ToggleButton("Add")
        self.obutton.connect('clicked', self.obutton_clicked)
        vbox.pack_end(self.button, False, False, 5)
        vbox.pack_end(self.obutton, False, False, 5)
        self.window.add(vbox)
        self.window.show_all()

    def get_command_corpus(self):
	self.corpus = {}
	for line in open("commandcorpus.cr").readlines():
		trueline = line[:-1]
		words = re.split("\s+",line)
		self.corpus[words[0].upper()] = words[1]

    def add_box(self,box,key,value):
	hbox = gtk.HBox()
	k = gtk.Entry()
	k.set_text(key)	
	t = gtk.Entry()
	t.set_text(value)
	hbox.pack_start(k)
	hbox.pack_start(t)
	hbox.show_all()
	box.pack_start(hbox)

    def show_boxes(self,box):
	for key in self.corpus.keys():
		self.add_box(box,key,self.corpus[key])		

    def generate_pair(self,a,b):
	return a + " " + b

    def generate_pairs(self,list1,list2):
	pairs = ""
	for i in range(len(list1)):
		pair = self.generate_pair(list1[i],list2[i])
		pairs += pair+"\n"
	return pairs[:-1]

    def change_command_corpus(self,pairs):
	file = open("commandcorpus.cr","w")
	for line in pairs:
		file.write(line)

    def change_corpus(self,list1):
	file = open("corpus.txt","w")
	for line in list1:
		file.write(line+"\n")

    def button_clicked(self, button):
        children = self.box.get_children()
	list1 = []
	list2 = []
	for child in children[:-2]:
		hchildren = child.get_children()
		c1 = hchildren[0].get_text()
		c2 = hchildren[1].get_text()
		list1.append(c1)
		list2.append(c2)

	pairs = self.generate_pairs(list1,list2)
	md = gtk.MessageDialog(None, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, 
            gtk.BUTTONS_OK_CANCEL, "Save this Configuration?")
        x = md.run()
	if x == gtk.RESPONSE_OK:
		print "Saving"
		self.change_command_corpus(pairs)
		self.change_corpus(list1)
		self.get_lm_and_dic()
        md.destroy()
    
	

    def obutton_clicked(self, button):
	self.add_box(self.box,"","")		

    def get_command_corpus(self):
	self.corpus = {}
	for line in open("commandcorpus.cr").readlines():
		trueline = line[:-1]
		words = re.split("\s+",line)
		self.corpus[words[0].upper()] = words[1]
	
    def get_lm_and_dic(self):
	main("corpus.txt")
			
class FileReader:
    def __init__(self, fp):
        self.fp = fp
    def read_callback(self, size):
        text = self.fp.read(size)
        text = text.strip()
        return text

def invokeSettings():
	app = Settings()
	gtk.main()
