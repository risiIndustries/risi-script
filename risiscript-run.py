#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
import dnf
import time
import argparse
import risiscript

if os.geteuid() == 0:
    print("For security reasons, do not run risiscript-run as root.")
    print("risiscript-run will automatically prompt you for root if needed.")

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
    for arg in args.arg:
        bash_args.append(arg)
    if root:
        bash_args.insert(0, root_command)

    subp = subprocess.run(bash_args, stderr=sys.stderr)
    sys.exit(subp.returncode)

if args.rootstdin:
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
        code = f"{code}{deps_root}dnf install -y {' '.join(script.metadata.dependencies)}\n\n"

    code = code + bash_code

    if script.metadata.root:
        sp = subprocess.Popen(
            sys.argv + ["--rootstdin"],
            stdin=subprocess.PIPE
        )
        sp.communicate(input=bytes(code, "utf-8"))
    else:
        run(False, code)
