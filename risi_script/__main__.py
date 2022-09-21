#!/usr/bin/env python3
import os
import subprocess
import tempfile
import yaml
import risi_script.constants as constants
from gi.repository import Gio

newline = "\n"
indent = "    "
saved_data = Gio.Settings.new("io.risi.script")
test_code = constants.test_code
class RisiScriptError(Exception):
    """Raised when something is wrong with your risi script code"""
    pass


class RisiScriptFailedCheckError(Exception):
    """Raised when a risi_script program fails a check"""
    pass


class Metadata:
    def __init__(self, metadata):
        self.dependencies = None
        for key in metadata:
            setattr(self, key, metadata[key])
        if "none" in str(self.dependencies).lower() or "null" in str(self.dependencies).lower():
            self.dependencies = None
        self.number_of_checks = {}


class Bash:
    def __init__(self, bash_code):
        bash_file_path = tempfile.mkstemp(prefix="risi_script-", suffix=".bash")[1]
        with open(bash_file_path, "w") as f:
            f.write(bash_code)
        sp = subprocess.run(["bash", bash_file_path], capture_output=True)
        os.remove(bash_file_path)

        self.subprocess = sp
        self.return_code = sp.returncode
        self.stdout = sp.stdout.decode()
        self.stderr = sp.stderr.decode()


class Script:
    def __init__(self, code):
        self.code = code
        self.parsed_code = yaml.safe_load(code)
        syntax_check(self.parsed_code)
        self.metadata = Metadata(self.parsed_code["metadata"])
        self.elements = {}

    def generate_script(self):  # Used to create a bash script from the risi_script file
        pass

    def get_elements(self, action, key_index):
        elements = []
        if "elements" in self.parsed_code[action].keys():
            for key in self.elements[action].keys():
                var_type = self.elements[action][key][0]
                if var_type not in ["WARNING", "DESCRIPTION", "TITLE"]:
                    args.append(str(key) + "=${" + str(key_index) + "}")
                    key_index += 1
        return elements

    def get_interactive_elements(self, action):
        return [
            x for x in self.get_elements(action)
            if element not in constants.non_interactive_elements
        ]
        
    def get_bash_arguments(self, action, key_index) -> list:
        args = []
        for element in self.get_interactive_elements():
            args.append(str(key) + "=${" + str(key_index) + "}")
            key_index += 1

    def get_actions(self):
        actions = []
        for action in self.parsed_code.keys():
            if action != "metadata":
                actions.append(action)
        return actions

    def get_available_actions(self):
        actions = []
        for action in self.get_actions():
            if "show" in self.parsed_code[action].keys():
                bash = Bash(self.parsed_code[action]["show"])
                if bash.return_code == 0:
                    actions.append(action)
            else:
                actions.append(action)
        return actions

    def check_action(self, action):
        if "checks" in self.parsed_code[action].keys():
            bash = Bash(self.parsed_code[action]["check"])
            if bash.return_code != 0:
                raise RisiScriptFailedCheckError(bash.stderr)


def syntax_check(parsed_code):
    # Checking Metadata
    if "metadata" not in parsed_code.keys():
        raise RisiScriptError("file must contain metadata function")
    elif "name" not in parsed_code["metadata"].keys():
        raise RisiScriptError("script name missing from metadata")
    elif "description" not in parsed_code["metadata"].keys():
        raise RisiScriptError("description missing from metadata")
    elif "dependencies" not in parsed_code["metadata"].keys():
        raise RisiScriptError("dependencies missing from metadata, add none for no dependencies")
    elif "tags" not in parsed_code["metadata"].keys():
        raise RisiScriptError("tags missing from metadata")
    elif "risiscript_version" not in parsed_code["metadata"].keys():
        raise RisiScriptError("risi_script version missing from metadata")

    # Checking for correct version
    elif parsed_code["metadata"]["risiscript_version"] != 2.0:
        raise RisiScriptError("risi_script version is deprecated."
                              "Please update your risi_script file.")

    # Checking for bash and checks options
    # for item in ["run", "install", "update", "remove"]:
    #     if item in parsed_code.keys():
    #         if "bash" not in parsed_code[item]:
    #             raise RisiScriptError(f"bash code missing from {item} action")
    #         if "checks" not in parsed_code[item]:
    #             raise RisiScriptError(f"checks missing from {item} function")
    #         # Making sure there's no "mode" variable in inputs to prevent errors
    #         if "init" in parsed_code[item] and "mode" in parsed_code[item]["init"]:
    #             raise RisiScriptError(f"{item} contains \"mode\" var_name")
def indent_newline(string):
    return string.replace("\n", "\n    ")

s = Script(test_code)