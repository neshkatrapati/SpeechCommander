#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk

from cmusphinx import *
from sphinxconfig import *

class HelloWorld:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_border_width(10)
    
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
    
        self.window.set_default_size(200,200)
        self.window.set_border_width(10)
        
	vbox = gtk.VBox()
	vbox.pack_start(gtk.Label("Welcome to SpeechCommander"))	
	
	hb = gtk.HBox()
	
	btn1 = gtk.Button("Launch App")	
	btn1.connect("clicked", self.launch_app)

	btn2 = gtk.Button("Launch Settings")
	btn2.connect("clicked", self.launch_settings)
	
	hb.pack_start(btn1,False,False,5)
	hb.pack_start(btn2,False,False,5)

	vbox.pack_start(hb)

	hb = gtk.HButtonBox()
	
	btn1 = gtk.Button("About")	
	btn2 = gtk.Button("Quit")
	btn2.connect("clicked", self.destroy)
	
	hb.add(btn1)
	hb.add(btn2)

	vbox.pack_start(hb)
        
	
        self.window.add(vbox)
        self.window.show_all()

    def launch_app(self,button):
	invoke()

    def launch_settings(self,button):
	invokeSettings()	

    def delete_event(self, widget, event, data=None):
        print "delete event occurred"

        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    hello = HelloWorld()
    hello.main()
