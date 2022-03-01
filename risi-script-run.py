#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import tempfile
import time

import risiscript

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--rootstdin", action="store_true")
arg_parser.add_argument("--run", type=str, action="store")
arg_parser.add_argument("--file", type=str, action="store")
arg_parser.add_argument("--gui", action="store_true")
arg_parser.add_argument("--arg", action="append")
args = arg_parser.parse_args()

run_args = ["run", "install", "update", "remove"]

root_command = "/bin/sudo"
if args.gui:
    root_command = "/bin/pkexec"

def run(root, code): # Creates a bash file code and runs it
    bash_file_path = tempfile.mkstemp()[1]
    with open(bash_file_path, "w") as file:
        file.write(code)

    bash_args = ["bash", bash_file_path]
    if args.run != "run":
        bash_args.append(args.run)
    if args.arg is not None:
        for arg in args.arg:
            bash_args.append(arg)

    subp = subprocess.run(bash_args, stderr=subprocess.PIPE, stdout=sys.stdout)
    sys.exit(subp.returncode)

if os.geteuid() == 0:
    time.sleep(0.1)
    run(True, sys.stdin.read())

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
            [root_command] + sys.argv + ["--rootstdin"],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdout=sys.stdout
        )
        sp.communicate(input=bytes(code, "utf-8"))
        sp.wait()
        sys.exit(sp.returncode)
    else:
        run(False, code)

