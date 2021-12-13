import yaml
import tempfile
import subprocess

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
  bash: |
    echo "hello world" |
  checks:
  - CHECKFORFILE:
    - file
  - CHECKINFILE:
    - file
    - "string"
  - CHECKOUTPUT:
    - ["bash", "command"] # Subprocess List for Python
    - "output"
  - CHECKOUTPUTLINE:
    - ["bash", "command"]
    - "output"
"""


class RisiScriptError(Exception):
    """Raised when something is wrong with your risi script code"""
    pass


class Metadata:
    def __init__(self, metadata):
        for key in metadata:
            setattr(self, key, metadata[key])
        if "none" in str(self.dependencies).lower() or "null" in str(self.dependencies).lower():
            self.dependencies = None


class Script:
    def __init__(self, code):
        parsed_code = yaml.safe_load(code)
        self.metadata = Metadata(parsed_code["metadata"])

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
        raise RisiScriptError("risiscript version missing from metadata")

    # Checking for conflicting functions
    elif "run" in parsed_code.keys() and "install" in parsed_code.keys():
        raise RisiScriptError("file cannot contain the run and install functions")
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


# name: "Test Script"
# description: "This is a test"
# dependencies:
# - test_dep
# root: false
# risiscript_version: 1
