import os
import yaml
import tempfile
import subprocess
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


class Script:
    def __init__(self, code):
        self.parsed_code = yaml.safe_load(code)
        syntax_check(self.parsed_code)
        self.metadata = Metadata(self.parsed_code["metadata"])
        self.installation_mode = "install" in self.parsed_code
        self.can_update = "update" in self.parsed_code
        self.installed = self.metadata.id in saved_data.get_value("installed-scripts")

        self.bash_file_path = tempfile.mkstemp()[1]

        if self.installation_mode:
            self.arguments = {
                "install": self.parsed_code["install"]["init"],
                "remove": self.parsed_code["remove"]["init"]
            }
            if self.can_update:
                self.arguments["update"] = self.parsed_code["update"]["init"]

        else:
            self.arguments = {"run": self.parsed_code["run"]["init"]}

    def code_to_script(self):  # Used to create a bash script from the risi-script file
        bash_file = open(self.bash_file_path, "a+")

        if self.installation_mode:  # Checks for installation script
            install_args = []  # Args from init function
            remove_args = []
            update_args = []

            key_index = 2  # Set to 2 because the 1st arg is reserved for ["install", "remove", "update"]
            for key in self.arguments["install"].keys():  # Getting variables from init function
                install_args.append(str(key) + " = $" + str(key_index))
                key_index += 1

            key_index = 2
            for key in self.arguments["remove"].keys():
                remove_args.append(str(key) + " = $" + str(key_index))
                key_index += 1

            if self.can_update:
                key_index = 2
                for key in self.arguments["update"].keys():
                    update_args.append(str(key) + " = $" + str(key_index))
                    key_index += 1

            file = f"""#!/bin/bash\n
if [$1 = "install"]; then\n
{indent_newline(indent + newline.join(install_args))}\n
{indent_newline(indent + self.parsed_code["install"]["bash"])}\nfi\n
if [$1 = "remove"]; then\n
{indent_newline(indent + newline.join(remove_args))}\n
{indent_newline(indent + self.parsed_code["remove"]["bash"])}\nfi"""

            if self.can_update:
                file = file + f"""\n\nif [$1 = "update"]; then\n
{indent_newline(indent + newline.join(update_args))}\n
{indent_newline(indent + self.parsed_code["update"]["bash"])}
fi"""

        else:
            run_args = []
            key_index = 1

            for key in self.arguments["run"].keys():
                run_args.append(str(key) + " = $" + str(key_index))
                key_index += 1

            file = f"""#!/bin/bash\n
{newline.join(run_args)}\n
{self.parsed_code["run"]["bash"]}"""

        bash_file.write(file)
        bash_file.close()

    def run_checks(self, parent):
        for item in self.parsed_code[parent]["checks"]:  # Note: items are dicts because of yaml weirdness
            if self.parsed_code[parent]["checks"][item][0] == "FILE":
                if not os.path.isfile(self.parsed_code[parent]["checks"][item][1]):
                    raise RisiScriptFailedCheckError(
                        f"file {self.parsed_code[parent]['checks'][item][1]} not found"
                    )
            elif self.parsed_code[parent]["checks"][item][0] == "FILECONTAINS":
                with open(self.parsed_code[parent]['checks'][item][1]) as f:
                    if not self.parsed_code[parent]['checks'][item][2] in f.read():
                        raise RisiScriptFailedCheckError("string {0 not found in file {1}".format(
                            self.parsed_code[parent]['checks'][item][1],
                            self.parsed_code[parent]['checks'][item][2]
                        ))
            elif (self.parsed_code[parent]["checks"][item][0] == "COMMANDOUTPUT" or
                  self.parsed_code[parent]["checks"][item][0] == "COMMANDOUTPUTCONTAINS"):

                subproc = subprocess.run(
                    self.parsed_code[parent]["checks"][item][1],
                    shell=True,
                    capture_output=True,
                    text=True,
                    universal_newlines=True
                )
                if subproc.returncode != 0:
                    raise RisiScriptFailedCheckError("command {0} threw error:\n{1}".format(
                        self.parsed_code[parent]["checks"][item][1],
                        subproc.stderr
                    ))
                elif (self.parsed_code[parent]["checks"][item][0] == "COMMANDOUTPUT" and
                      self.parsed_code[parent]["checks"][item][2] != subproc.stdout):
                    raise RisiScriptFailedCheckError("string {0} doesn't match output of {1}".format(
                        self.parsed_code[parent]["checks"][item][2],
                        self.parsed_code[parent]["checks"][item][1]
                    ))
                elif (self.parsed_code[parent]["checks"][item][0] == "COMMANDOUTPUTCONTAINS" or
                      self.parsed_code[parent]["checks"][item][2] in subproc.stdout):
                    raise RisiScriptFailedCheckError("string {0} doesn't contain output of {1}".format(
                        self.parsed_code[parent]["checks"][item][2],
                        self.parsed_code[parent]["checks"][item][1]
                    ))


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
            # Making sure there's no "mode" variable in inputs to prevent errors
            if "init" in parsed_code[item] and "mode" in parsed_code[item]["init"]:
                raise RisiScriptError(f"{item} contains \"mode\" var_name")


def indent_newline(string):
    return string.replace("\n", "\n    ")
