#!/usr/bin/python3
import risi_script
import threading

gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "3.91")
gi.require_version("Adw", "1")
from gi.repository import Gtk, GLib, Vte, Adw


class ElementData:
    def __init__(self, element, value=None):
        self.element = element
        self.value = value

class InteractiveElement:
    def __init__(self):
        # Must be implemented by child class
        self.error = False
        if type(self) == InteractiveElementRow:
            raise NotImplementedError("InteractiveElementRow is abstract class")

    def get_value(self):
        # Must be implemented by child class
        raise NotImplementedError("InteractiveElementRow is abstract class")

    def check_if_valid(self):
        return True  # Returns true if not implemented
        if type(self) == InteractiveElementRow:
            raise NotImplementedError("InteractiveElementRow is abstract class")

    def set_error(self, error: False):
        # Must be implemented by child class
        if type(self) == InteractiveElementRow:
            raise NotImplementedError("InteractiveElementRow is abstract class")


class NonInteractiveElement(InteractiveElement):
    def __init__(self):
        super().__init__()
        self.error = False

    def get_value(self):
        return None

    def set_error(self, error: False):
        self.error = False

    def check_if_valid(self):
        return True



class InteractiveElementsPage(Adw.PreferencesPage):
    def __init__(self, elements: list):
        super().__init__()
        self.elements = elements
        self.group = Adw.PreferencesGroup()
        if elements


