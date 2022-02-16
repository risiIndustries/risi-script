#!/usr/bin/env python3
import os, yaml, tempfile, subprocess
from gi.repository import Gio

newline = "\n"
indent = "    "
saved_data = Gio.Settings.new("io.risi.script")


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


class Script:
    def __init__(self, code):
        self.code = code
        self.parsed_code = yaml.safe_load(code)
        syntax_check(self.parsed_code)
        self.metadata = Metadata(self.parsed_code["metadata"])
        self.installation_mode = "install" in self.parsed_code
        self.can_update = "update" in self.parsed_code
        self.installed = self.metadata.id in saved_data.get_strv("installed-scripts")

        self.bash_file_path = tempfile.mkstemp()[1]

        self.arguments = {}
        if self.installation_mode:
            try:
                self.arguments["install"] = self.parsed_code["install"]["init"]
            except KeyError:
                self.arguments["install"] = None

            try:
                self.arguments["remove"] = self.parsed_code["remove"]["init"]
            except KeyError:
                self.arguments["remove"] = None

            self.metadata.number_of_checks = {
                "install": len(self.parsed_code["install"]["checks"]),
                "remove": len(self.parsed_code["remove"]["checks"])
            }

            if self.can_update:
                try:
                    self.arguments["update"] = self.parsed_code["update"]["init"]
                except KeyError:
                    self.arguments["update"] = None
                self.metadata.number_of_checks["update"] = len(self.parsed_code["update"]["checks"])

            if self.can_update:
                self.arguments["update"] = self.parsed_code["update"]["init"]

        else:
            try:
                self.arguments = {"run": self.parsed_code["run"]["init"]}
            except KeyError:
                self.arguments["run"] = None

            self.metadata.number_of_checks = {
                "run": len(self.parsed_code["run"]["checks"])
            }

    def code_to_script(self):  # Used to create a bash script from the risi-script file
        bash_file = open(self.bash_file_path, "a+")

        if self.installation_mode:  # Checks for installation script
            install_args = []  # Args from init function
            remove_args = []
            update_args = []

            key_index = 2  # Set to 2 because the 1st arg is reserved for ["install", "remove", "update"]
            for key in self.arguments["install"].keys():  # Getting variables from init function
                install_args.append(str(key) + "=$" + str(key_index))
                key_index += 1

            key_index = 2
            for key in self.arguments["remove"].keys():
                remove_args.append(str(key) + "=$" + str(key_index))
                key_index += 1

            if self.can_update:
                key_index = 2
                for key in self.arguments["update"].keys():
                    update_args.append(str(key) + "=$" + str(key_index))
                    key_index += 1

            bash = f"""if [ $1 = "install" ]; then\n
{indent_newline(indent + newline.join(install_args))}\n
{indent_newline(indent + self.parsed_code["install"]["bash"])}\nfi\n
if [ $1 = "remove" ]; then\n
{indent_newline(indent + newline.join(remove_args))}\n
{indent_newline(indent + self.parsed_code["remove"]["bash"])}\nfi"""

            if self.can_update:
                bash = bash + f"""\n\nif [ $1 = "update" ]; then\n
{indent_newline(indent + newline.join(update_args))}\n
{indent_newline(indent + self.parsed_code["update"]["bash"])}
fi"""

        else:
            try:
                run_args = []
                key_index = 1

                for key in self.arguments["run"].keys():
                    run_args.append(str(key) + "=$" + str(key_index))
                    key_index += 1
            except (TypeError, AttributeError):
                run_args = []

            bash = f"""#!/bin/bash\n
{newline.join(run_args)}\n
{self.parsed_code["run"]["bash"]}"""

        return bash

    def run_checks(self, parent, arg_outputs, pulse_function=None):
        for item in self.parsed_code[parent]["checks"]:  # Note: items are dicts because of yaml weirdness
            args = list(item.values())[0]
            new_args = []

            for arg in args:
                new_arg = arg
                for i in arg_outputs:
                    new_arg = new_arg.replace(f"${i}", str(arg_outputs[i]))
                new_args.append(new_arg)

            args = new_args

            # print(list(item.values())[0])
            if list(item.keys())[0] == "FILE":
                if not os.path.isfile(args[0]):
                    raise RisiScriptFailedCheckError(f"file {args[0]} not found")
            elif list(item)[0] == "FILECONTAINS":
                if os.path.isfile(args[0]):
                    with open(args[0]) as f:
                        if not args[1] in f.read():
                            raise RisiScriptFailedCheckError("string '{0}' not found in file '{1}'".format(
                                args[0],
                                args[1]
                            ))
            elif list(item)[0] in ["COMMANDOUTPUT", "COMMANDOUTPUTCONTAINS"]:
                subproc = subprocess.run(
                    args[0],
                    shell=True,
                    capture_output=True,
                    text=True,
                    universal_newlines=True
                )
                if subproc.returncode != 0:
                    raise RisiScriptFailedCheckError("command '{0}' threw error:\n{1}".format(
                        args[0],
                        subproc.stderr
                    ))
                elif list(item.keys())[0] == "COMMANDOUTPUT" and args[1] != subproc.stdout:
                    print("meme")
                    raise RisiScriptFailedCheckError("string '{0}' doesn't match output of '{1}'".format(
                        args[1],
                        args[0]
                    ))
                elif list(item.keys())[0] == "COMMANDOUTPUTCONTAINS" and args[1] not in subproc.stdout:
                    raise RisiScriptFailedCheckError("string '{0}' doesn't contain output of '{1}'".format(
                        args[1],
                        args[0]
                    ))
            if pulse_function is not None:
                pulse_function()


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
    elif "run" not in parsed_code.keys() and "install" not in parsed_code.keys():
        raise RisiScriptError("missing run or install function")
    elif "install" in parsed_code.keys() and "remove" not in parsed_code.keys():
        raise RisiScriptError("remove function detected without install function")
    elif "update" in parsed_code.keys() and "install" not in parsed_code.keys():
        raise RisiScriptError("update function detected without install function")

    # Checking for bash and checks options
    for item in ["run", "install", "update", "remove"]:
        if item in parsed_code.keys():
            if "bash" not in parsed_code[item]:
                raise RisiScriptError(f"bash code missing from {item} function")
            if "checks" not in parsed_code[item]:
                raise RisiScriptError(f"checks missing from {item} function")
            # Making sure there's no "mode" variable in inputs to prevent errors
            if "init" in parsed_code[item] and "mode" in parsed_code[item]["init"]:
                raise RisiScriptError(f"{item} contains \"mode\" var_name")


def indent_newline(string):
    return string.replace("\n", "\n    ")

