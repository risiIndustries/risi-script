#!/usr/bin/python3
import argparse
import os
import subprocess
import risi_script
import gi
import time
import threading
from copy import deepcopy

gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "3.91")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GLib, Vte, Adw

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--file", type=str, action="store")
arg_parser.add_argument("--action", type=str, action="store")
parsed_args = arg_parser.parse_args()

_BUILDER_FILE = os.path.dirname(os.path.abspath(__file__)) + "/rs2.xml"

if parsed_args.file:
    if not os.path.isfile(parsed_args.file):
        print(f"File, {parsed_args.file} doesn't exist")
        exit()
else:
    print("Please provide risi_script file")
    exit()

with open(parsed_args.file, "r") as script_file:
    script = risi_script.Script(script_file)


class Application(Adw.Application):
    def __init__(self, script, *args, **kwargs):
        super().__init__(*args, application_id='io.risi.script', **kwargs)
        self.script = script
        self.builder = Gtk.Builder()
        self.builder.add_from_file(_BUILDER_FILE)
        self.window = self.builder.get_object("main_window")
        self.actions = []

    def do_activate(self):
        self.window.set_application(self)
        self.window.present()

        # Setting metadata
        self.builder.get_object("name").set_subtitle(self.script.metadata.name)
        self.builder.get_object("id").set_subtitle(self.script.metadata.id)
        self.builder.get_object("short_description").set_subtitle(self.script.metadata.short_description)
        self.builder.get_object("description").set_label(self.script.metadata.description)
        self.builder.get_object("rs_version").set_subtitle(self.script.metadata.rs_version)

        # Add dependencies and flags
        dependencies_view = self.builder.get_object("dependencies")
        if len(self.script.metadata.dependencies) == 0:
            dependencies_view.get_object("dependencies").set_enable_expansion(False)
        else:
            for dependency in self.script.metadata.dependencies:
                dependencies_view.add_row(expander_label(dependency))
        if len(self.script.metadata.dependencies) == 1:
            dependencies_view.set_subtitle("1 Dependency")
        else:
            dependencies_view.set_subtitle(f"{len(self.script.metadata.dependencies)} Dependencies")

        flags_view = self.builder.get_object("flags")
        if len(self.script.metadata.flags) == 0:
            flags_view.get_object("flags").set_enable_expansion(False)
        else:
            for flag in self.script.metadata.flags:
                flags_view.add_row(expander_label(flag))

        # Trust level
        trusted_widget = self.builder.get_object("trusted")
        if self.script.trusted:
            trusted_widget.set_subtitle("Trusted")
            trusted_widget.add_css_class("success")
            trusted_widget.add_prefix(
                Gtk.Image.new_from_icon_name("security-high-symbolic")
            )          
        else:
            trusted_widget.set_subtitle("Not Trusted")
            trusted_widget.add_css_class("error")
            trusted_widget.add_prefix(
                Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            )

        action_thread = threading.Thread(target=self.load_actions)
        action_thread.start()

    def load_actions(self):
        self.actions = self.script.get_available_actions()
        GLib.idle_add(self.add_actions)

    def add_actions(self):
        for action in self.actions:
            self.builder.get_object("actionGroup").add(
                ScriptActionRow(self.script, action)
            )
        self.builder.get_object("actionStack").set_visible_child(
          self.builder.get_object("actionPage")
        )
        
        

class ScriptActionRow(Adw.ActionRow):
    def __init__(self, script, action):
        super().__init__()
        self.script = script
        self.action = action
        self.set_title(script.get_action_display_name(action))
            


def expander_label(text):
    label = Gtk.Label(xalign=0)
    label.set_text(text)
    label.set_margin_start(12)
    label.set_margin_end(12)
    label.set_margin_top(12)
    label.set_margin_bottom(12)
    return label





app = Application(script)
app.run(None)
