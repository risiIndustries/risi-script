#!/usr/bin/env python3
import os
import subprocess
import tempfile
import yaml
import risi_script.constants as constants
from gi.repository import Gio

newline = "\n"
indent = "    "

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


def install_dependencies(dependencies):
    if dependencies is not None:
        print("Check dependencies...")
        depend_proc = subprocess.run(["rpm", "-qa", "--qf", "%{NAME}\n"], stdout=subprocess.PIPE)
        installed_dependencies = depend_proc.stdout.decode('utf-8').split("\n")
        packages = [x for x in dependencies if x not in installed_dependencies]
        proc = ["dnf", "install", "-y"] + packages
        # Add sudo
        if os.geteuid() != 0:
            proc = ["pkexec"] + proc
        subprocess.run(proc)

        print("Checking if dependencies installed correctly...")
        depend_proc = subprocess.run(["rpm", "-qa", "--qf", "%{NAME}\n"], stdout=subprocess.PIPE)
        installed_dependencies = depend_proc.stdout.decode('utf-8').split("\n")
        for package in packages:
            if package not in installed_dependencies:
                raise RisiScriptError(f"Failed to install {package}")
                print("Failed to install " + package)
    return False, None


class Bash:
    def __init__(self, bash_code: str, root=False, interactive_elements=None):
        self.root = root

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

    def run_code(self, action, interactive_elements):  # Used to create a bash script from the risi_script file
        # Install dependencies
        self.elements = self.get_elements(action)
        install_dependencies(self.metadata.dependencies)

        # Run code from action
        bash_code = "#!/bin/bash\n"
        for element in self.get_bash_arguments(action):
            bash_code += element + "\n"
        bash_code += self.parsed_code[action]["bash"]
        Bash(
            bash_code,
            root="root" in self.parsed_code["flags"],
            interactive_elements=interactive_elements
        )

        # Run checks if they exist
        self.check_action(action)

    def get_elements(self, action):
        elements = []
        if "elements" in self.parsed_code[action].keys():
            elements = self.parsed_code[action]["elements"]
        return elements

    def get_interactive_elements(self, action):
        print(self.get_elements(action))
        items = [
            x[x] for x in self.get_elements(action)
            if x[x] not in constants.non_interactive_elements
        ]
        for i in items:
            print(self.elements[i][0])
        print(items)
        return items

    def get_bash_arguments(self, action) -> list:
        key_index = 1
        args = []
        for element in self.get_interactive_elements(action):
            args.append(str(element) + "=${" + str(key_index) + "}")
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

    def check_action(self, action, interactive_elements):
        if "checks" in self.parsed_code[action].keys():
            print("Running checks...")
            bash_code = "#!/bin/bash\n"
            for element in self.get_bash_arguments(action):
                bash_code += element + "\n"
            bash_code += self.parsed_code[action]["bash"]
            bash = Bash(
                bash_code,
                root="root" in self.parsed_code["flags"],
                interactive_elements=interactive_elements
            )
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
    elif "flags" not in parsed_code["metadata"].keys():
        print(parsed_code["metadata"])
        raise RisiScriptError("flags missing from metadata")
    elif "risiscript_version" not in parsed_code["metadata"].keys():
        raise RisiScriptError("risiscript_version missing from metadata")

    # Checking for correct version
    elif parsed_code["metadata"]["risiscript_version"] != 2.0:
        raise RisiScriptError("The set risiscript_version is deprecated."
                              "Please update your risiscript file.")

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