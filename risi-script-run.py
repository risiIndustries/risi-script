#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import tempfile
import time

import risiscript

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--run", type=str, action="store")
arg_parser.add_argument("--file", type=str, action="store")
arg_parser.add_argument("--gui", action="store_true")
arg_parser.add_argument("--arg", action="append")
args = arg_parser.parse_args()

run_args = ["run", "install", "update", "remove"]

root_command = "/bin/sudo"
if args.gui:
    root_command = "/bin/pkexec"


def run(rcode):  # Creates a bash file code and runs it
    bash_file_path = tempfile.mkstemp()[1]
    with open(bash_file_path, "w") as f:
        f.write(rcode)

    bash_args = ["bash", bash_file_path]
    if args.run != "run":
        bash_args.append(args.run)
    if args.arg is not None:
        for arg in args.arg:
            bash_args.append(arg)

    subp = subprocess.run(bash_args, stderr=subprocess.PIPE, stdout=sys.stdout)
    return subp.returncode


if os.geteuid() == 0:
    time.sleep(0.1)
    sys.exit(run(sys.stdin.read()))
elif args.run in run_args:
    with open(args.file, "r") as file:
        script = risiscript.Script(file.read())

    bash_code = script.code_to_script()
    code = "#!/bin/bash\n"

    if script.metadata.dependencies is not None:
        deps_root = root_command + " "
        if script.metadata.root:
            deps_root = ""
        code = f"{code}{deps_root}dnf install -y {' '.join(script.metadata.dependencies)} || exit $?\n\n"

        code = code + bash_code

    if script.metadata.root:
        sp = subprocess.Popen(
            [root_command] + sys.argv,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdout=sys.stdout
        )
        sp.communicate(input=bytes(code, "utf-8"))
        sp.wait()
        return_code = sp.returncode
    else:
        return_code = run(code)

    reboot = False
    if hasattr(script, "reboot"):
        reboot = script.reboot and args.gui and return_code == 0
    if reboot:
        reboot_question = input("This script requires a reboot. Would you like to reboot now? (y/n)\n")
        if reboot_question.lower() == "yes" or reboot_question.lower() == "y":
            subprocess.run(["reboot", "now"], stdout=sys.stdout)
        else:
            print("Not rebooting")

    sys.exit(return_code)
