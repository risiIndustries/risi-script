import yaml
import tempfile
import subprocess
import os

test = """
metadata:
  name: "ScriptName"
  description: "Description of what the script does"
  dependencies:
    - package1
    - package2
  root: true
  risiscript_version: 1
run: # Conflicts with install function
  init:
    - ENTRY:
      - "var_name" # variable name for bash script
      - "Please enter something" # Question for user
    - ENTRY:
      - "Please enter another thing" # Question for user
    - FILE:
      - "Please select a file" # Question for user
      - "~/" # Starting dir
      - ".txt" # ex: *.txt. Use * for any type of file
    - DIRECTORY:
      - "Please select a directory"  # Question for user
      - "~/" # Starting dir
    - CHOICE:
      - "Please choose this" # Question for users
      - [ "Choice1", "Choice2" ] # The choices for a user to pick
  bash: |
    echo "hello world"
  checks:
  - CHECKFORFILE:
    - file
  - CHECKINFILE:
    - file
    - "string"
  - CHECKOUTPUT:
    - ["bash", "command"] # Subprocess List for Python
    - "output"
  - CHECKINOUTPUT:
    - ["bash", "command"]
    - "output"
"""


class RisiScriptError(Exception):
    """Raised when something is wrong with your risi script code"""
    pass


class Metadata:
    def __init__(self, metadata):
        self.dependencies = None
        for key in metadata:
            setattr(self, key, metadata[key])
        if "none" in str(self.dependencies).lower() or "null" in str(self.dependencies).lower():
            self.dependencies = None


class Script:
    def __init__(self, code):
        input_functions = {
            "ENTRY": self.entry_input,
            "FILE": self.file_input,
            "DIRECTORY": self.directory_input,
            "CHOICE": self.choice_input
        }

        self.parsed_code = yaml.safe_load(code)
        syntax_check(self.parsed_code)
        self.metadata = Metadata(self.parsed_code["metadata"])
        self.installation_mode = "install" in self.parsed_code

        self.bash_file_path = tempfile.mkstemp()[1]
        self.bash_file = open(self.bash_file_path, "a+")
        self.arguments = []

    def run(self):
        subprocess.Popen(["bash", self.bash_file_path])

    def entry_input(self, parameters):
        pass

    def file_input(self, parameters):
        pass

    def directory_input(self, parameters):
        pass

    def choice_input(self, parameters):
        pass

    def code_to_script(self):
        if self.installation_mode:
            pass
        else:
            for item in get_init_args("run", self.parsed_code):
                self.bash_file.write(item)
                print(item)
            print(self.parsed_code["run"]["bash"])
            self.bash_file.write(self.parsed_code["run"]["bash"])
        os.system("cat " + self.bash_file_path)

        # dependencies: sudo dnf install -y []
        # make it check for either a run, or [install, remove, update] functions, and put the code from those into the file


def get_init_args(parent, parsed_code):
    arg_list = []
    arg_index = 1
    for item in parsed_code[parent]["init"]:
        if list(item.keys())[0] in ["ENTRY", "FILE", "DIRECTORY", "CHOICE"]:
            arg_type = list(parsed_code[parent]["init"][0].keys())[0]
            arg_list.append(
                str(parsed_code[parent]["init"][0][arg_type][0]) +
                " = $" + str(arg_index)
            )
            arg_index += 1
    return arg_list

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
    elif "root" not in parsed_code["metadata"].keys():
        raise RisiScriptError("root missing from metadata")
    elif "risiscript_version" not in parsed_code["metadata"].keys():
        raise RisiScriptError("risi-script version missing from metadata")

    # Checking for conflicting functions
    elif "run" in parsed_code.keys() and "install" in parsed_code.keys():
        raise RisiScriptError("file cannot contain both the run and install functions")
    elif "install" in parsed_code.keys() and "remove" not in parsed_code.keys():
        raise RisiScriptError("update function detected without install function")
    elif "update" in parsed_code.keys() and "install" not in parsed_code.keys():
        raise RisiScriptError("update function detected without install function")

    # Checking for bash and checks options
    for item in ["run", "install", "update", "remove"]:
        if item in parsed_code.keys():
            if "bash" not in parsed_code[item]:
                raise RisiScriptError(f"bash code missing from {item} function")
            if "checks" not in parsed_code[item]:
                raise RisiScriptError(f"checks missing from {item} function")

script = Script(test)
#print(script.parsed_code)
script.code_to_script()

# name: "Test Script"
# description: "This is a test"
# dependencies:
# - test_dep
# root: false
# risiscript_version: 1
