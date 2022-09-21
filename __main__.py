#!/usr/bin/env python3
import os
import subprocess
import tempfile
import yaml
from gi.repository import Gio

newline = "\n"
indent = "    "
saved_data = Gio.Settings.new("io.risi.script")
test_code = """#!/bin/risi-script
#!/bin/risi-script
metadata:
  risiscript_version: 2.0
  name: "ScriptName"
  id: "com.example.scriptname"
  description: "Description of what the script does"
  dependencies: # Just put None for no dependencies
    - package1
    - package2
  tags: [root, reboot]


action: # Requires remove function
  show: |  # Only shows if the exit code is 0
    echo "Hello World"
    exit 0
  elements:
    entry_var:
      - ENTRY # Type of init var...
      - "Please enter something" # Question for user
    file_var:
      - FILE
      - "Please select a file" # Question for user
      - ".txt" # ex: *.txt. Use * for any type of file
    directory_var:
      - DIRECTORY
      - "Please select a directory"  # Question for user
    choice_var:
      - CHOICE
      - "Please choose this" # Question for users
      - [ "Choice1", "Choice2" ] # The choices for a user to pick
    boolean_var:
      - BOOLEAN
      - "Toggle this"
      - True
    warning:
      - WARNING
      - "Warning"
      - "This is a warning description"
  run: |
    echo "hello world"
  checks: | # Check if it runs
    ""
"""

class RisiScriptError(Exception):
    """Raised when something is wrong with your risi script code"""
    pass


class RisiScriptFailedCheckError(Exception):
    """Raised when a risi-script program fails a check"""
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
        bash_file_path = tempfile.mkstemp(prefix="risi-script-", suffix=".bash")[1]
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
        self.arguments = {}

    def code_to_script(self):  # Used to create a bash script from the risi-script file
        pass

    def get_elements(self, action, key_index):
        args = []
            if self.arguments[action] is not None:
            for key in self.arguments[action].keys():
                var_type = self.arguments[action][key][0]
                if var_type not in ["WARNING", "DESCRIPTION", "TITLE"]:
                    args.append(str(key) + "=${" + str(key_index) + "}")
                    key_index += 1
        return args


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
    print(parsed_code)
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
        raise RisiScriptError("risi-script version missing from metadata")

    # Checking for correct version
    elif parsed_code["metadata"]["risiscript_version"] != 2.0:
        raise RisiScriptError("risi-script version is deprecated."
                              "Please update your risi-script file.")

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
print(s.get_available_actions())