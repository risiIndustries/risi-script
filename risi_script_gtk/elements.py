#!/usr/bin/python3
import risi_script
import gi
import time
import threading
from copy import deepcopy

gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "3.91")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GLib, Vte, Adw

