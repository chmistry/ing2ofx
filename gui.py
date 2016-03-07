#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gui.py
#
#  Copyright 2013,2016 Arie van Dobben <avandobben@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import time
import ing2ofx
import os


class Handler:

    def __init__(self, gui):
        self.gui = gui

    def on_window1_delete_event(self, *args):
        Gtk.main_quit(*args)

    def on_button1_clicked(self, button1):
        while True:
            convert = self.gui.builder.get_object("checkbutton1").get_active()
            convert_date = self.gui.builder.get_object(
                "checkbutton2").get_active()
            csvfile = self.gui.builder.get_object(
                "filechooserbutton1").get_filename()
            if not csvfile:
                self.gui.statusbar_push("No csv file chosen!")
                break

            outdir = self.gui.builder.get_object(
                "filechooserbutton2").get_current_folder()
            if self.gui.builder.get_object("checkbutton3").get_active():
                outfile = os.path.basename(csvfile)
            else:
                outfile = self.gui.builder.get_object("entry1").get_text()

            self.gui.push_text("Input:\n\tconvert: " + str(convert) + 
                               "\n\t convert_date: " + str(convert_date) + 
                               "\n\t csvfile: " + str(csvfile) +
                               "\n\t outdir: " + str(outdir) + 
                               "\n\t outfile: " + str(outfile))

            convert = CsvConverter(
                csvfile=csvfile, outfile=outfile, dir=outdir, convert=convert,
                convert_date=convert_date)

            self.gui.push_text(convert.stats_transactions + 
                                "\n\t" + convert.stats_in +
                                "\n\t" + convert.stats_out)
            break

    def on_filechooserbutton1_file_set(self, button):
        self.gui.statusbar_push("File %s selected" % button.get_filename())
        self.gui.push_text("File %s selected" % button.get_filename())

    def on_imagemenuitem5_activate(self, *args):
        Gtk.main_quit(*args)

    def on_imagemenuitem10_activate(self, menuitem):
        aboutwindow = self.gui.builder.get_object("aboutdialog1")
        aboutwindow.run()

    def on_aboutdialog1_response(self, dialog, response):
        dialog.hide()

    def on_checkbutton3_toggled(self, button):
        if button.get_active():
            self.gui.builder.get_object("entry1").set_editable(False)
        else:
            self.gui.builder.get_object("entry1").set_editable(True)


class Gui:

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("gui.glade")
        self.builder.connect_signals(Handler(self))
        self.window = self.builder.get_object("window1")
        self.window.show_all()
        self.text = ""
        self.push_text("Program Started")
        self.builder.get_object(
            "filechooserbutton2").set_current_folder("./ofx")
        Gtk.main()

    def push_text(self, text):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        self.text += (now + " - " + text + "\n")
        self.builder.get_object("textbuffer1").set_text(self.text)

    def statusbar_push(self, text):
        context = self.builder.get_object("statusbar1").get_context_id(text)
        self.builder.get_object("statusbar1").push(context, text)


class Arguments_container:

    def __init__(self):
        self.outfile = None
        self.csvfile = None
        self.dir = None
        self.convert = None
        self.convert_date = None


class CsvConverter:

    def __init__(self, csvfile, outfile, dir='./ofx', convert=False,
                 convert_date=False):

        self.args = Arguments_container()
        self.args.outfile = outfile
        self.args.csvfile = csvfile
        self.args.dir = dir
        self.args.convert = convert
        self.args.convert_date = convert_date

        ofx = ing2ofx.OfxWriter(self.args, gui=True)

        self.stats_transactions = ofx.stats_transactions
        self.stats_in = ofx.stats_in
        self.stats_out = ofx.stats_out

if __name__ == "__main__":
    gui = Gui()
