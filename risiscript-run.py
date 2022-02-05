#!/usr/bin/env python3
import sys
import subprocess
import tempfile
import dnf

run_args = ["run", "install", "update", "remove"]
if sys.argv[1] in run_args:
    bash_file_path = tempfile.mkstemp()[1]
    code = sys.stdin.read()
    with open(bash_file_path, "w") as file:
        file.write(code)

    args = ["bash", bash_file_path]
    for arg in sys.argv[1:]:
        if arg != "run" and sys.argv.index(arg) != 1:
            arg.append(arg)
    subp = subprocess.run(args, stderr=sys.stderr)
    sys.exit(subp.returncode)

    if not one_time_use:
        if not os.path.isdir(os.path.expanduser('~') + "/.risiscripts"):
            os.makedirs(os.path.expanduser('~') + "/.risiscripts")

elif sys.argv[1] == "deps":
    to_install = []

    base = dnf.Base()
    base.fill_sack()
    q = base.sack.query()
    installed = list(q.installed())

    deps = sys.argv[2:]
    for dep in deps:
        if dep not in installed:
            to_install.append(dep)
    if to_install != None or to_install != []:
        subp = subprocess.run(["dnf", "install", "-y"] + to_install, stderr=sys.stderr)
        sys.exit(subp.returncode)