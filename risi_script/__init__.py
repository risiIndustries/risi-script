#!/usr/bin/env python3
import os
import subprocess
import tempfile
import warnings

import yaml
import risi_script.constants as constants
from gi.repository import Gio

newline = "\n"
indent = "    "
bashrc = os.path.dirname(os.path.abspath(__file__)) + "/risiscriptrc.sh"


class RisiScriptError(Exception):
    """Raised when something is wrong with your risi script code"""
    pass


class RisiScriptFailedCheckError(Exception):
    """Raised when a risi_script program fails a check"""
    pass


class Metadata:
    def __init__(self, metadata):
        self.name = str(metadata["name"])
        self.description = str(metadata["description"])
        self.id = str(metadata["id"])
        self.rs_version = str(metadata["rs_version"])
        self.flags = metadata["flags"]

        if "short_description" in metadata and metadata["short_description"] is not None and \
                metadata["short_description"] != "None":
            self.short_description = str(metadata["short_description"])
        else:
            self.short_description = self.description

        if "dependencies" in metadata and metadata["dependencies"] is not None and metadata["dependencies"] != "None":
            self.dependencies = metadata["dependencies"]
        else:
            self.dependencies = []


def install_dependencies(dependencies):
    if dependencies is not None:
        print("Check dependencies...")
        depend_proc = subprocess.run(["rpm", "-qa", "--qf", "%{NAME}\n"], stdout=subprocess.PIPE)
        installed_dependencies = depend_proc.stdout.decode('utf-8').split("\n")
        packages = [x for x in dependencies if x not in installed_dependencies]

        if len(packages) > 0:
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


class Bash:
    def __init__(self, bash_code: str, root=False, interactive_elements=None):
        self.root = root

        if interactive_elements is None:
            interactive_elements = []

        bash_file_path = tempfile.mkstemp(prefix="risi_script-", suffix=".bash")[1]
        with open(bash_file_path, "w") as f:
            f.write(bash_code)
            f.close()
        print(bash_code)
        sp = subprocess.Popen(["bash", bash_file_path] + interactive_elements)

        self.subprocess = sp
        self.stdout, self.stderr = sp.communicate()
        self.return_code = sp.returncode
        os.remove(bash_file_path)


class Script:
    def __init__(self, code):
        self.code = code
        self.parsed_code = yaml.safe_load(code)
        syntax_check(self.parsed_code)
        self.metadata = Metadata(self.parsed_code["metadata"])

        # This feature is not implemented yet
        self.trusted = False

        self.elements = {}
        for action in self.get_actions():
            self.elements[action] = self.get_elements(action)

    def run_code(self, action, interactive_elements):  # Used to create a bash script from the risi_script file
        # Install dependencies
        self.elements = self.get_elements(action)
        install_dependencies(self.metadata.dependencies)

        # Run code from action
        bash_code = f'#!/bin/bash\nsource {bashrc}\n'
        for element in self.get_bash_arguments(action):
            bash_code += element + "\n"
        bash_code += self.parsed_code[action]["run"]
        process = Bash(
            bash_code,
            root="root" in self.metadata.flags,
            interactive_elements=interactive_elements
        )

        # Run checks if they exist
        print(process.stderr)
        print(process.stdout)
        self.check_action(action, interactive_elements)

    def get_elements(self, action):
        if "elements" in self.parsed_code[action].keys():
            elements = self.parsed_code[action]["elements"]
        return elements

    def get_interactive_elements(self, action):
        elements = self.get_elements(action)
        items = {}
        for x in elements:
            if elements[x][0] not in constants.non_interactive_elements:
                items[x] = elements[x]
        return items

    def get_bash_arguments(self, action) -> list:
        key_index = 1
        args = []
        for element in self.get_interactive_elements(action):
            print(element)
            args.append(str(element) + "=${" + str(key_index) + "}")
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
            if "show" in self.parsed_code[action]:
                bash = Bash(self.parsed_code[action]["show"])
                if bash.return_code == 0:
                    actions.append(action)
            else:
                actions.append(action)
        return actions

    def get_action_display_name(self, action):
        if "name" in self.parsed_code[action].keys():
            return self.parsed_code[action]["name"]
        else:
            return action

    def check_action(self, action, interactive_elements):
        if "check" in self.parsed_code[action].keys():
            print("Running checks...")
            bash_code = f"#!/bin/bash\nsource {bashrc}\nrs-status \"Running checks...\"\n"
            for element in self.get_bash_arguments(action):
                bash_code += element + "\n"
            bash_code += self.parsed_code[action]["check"]
            bash = Bash(
                bash_code,
                root=("root" in self.metadata.flags),
                interactive_elements=interactive_elements
            )
            print(bash.return_code)
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
    elif "short_description" not in parsed_code["metadata"].keys():
        warnings.warn("short_description missing from metadata. Using description instead")
    elif "rs_version" not in parsed_code["metadata"].keys():
        warnings.warn(f"Warning: rs_version not specified in metadata. Assuming {constants.current_version}")

    # Checking for correct version
    if str(parsed_code["metadata"]["rs_version"]) not in constants.supported_versions:
        if str(parsed_code["metadata"]["rs_version"]) == "1.0":
            raise RisiScriptError("This script is written for risi_script 1.0, which is no longer supported. "
                                  "Please update the script to the latest version of risi_script.")
        else:
            raise RisiScriptError(f'This script is written for an unsupported version of risi_script: '
                                  f'{parsed_code["metadata"]["rs_version"]}')

def indent_newline(string):
    return string.replace("\n", "\n    ")
