import tempfile
import subprocess

# Input functions
simplefunctions = {
  "@INPUT": 'echo "@INPUT Ran"',
  "@FILE": 'echo "@FILE Ran"',
  "@DIRECTORY": 'echo "@DIRECTORY Ran"',
  "@CHOICE": 'echo "@CHOICE Ran"',
  "@CHECKFORFILE": 'python3 bashinterface.py CHECKFORFILE',
  "@CHECKINFILE": 'echo "@CHECKINFILE Ran"',
  "@CHECKOUTPUT": 'echo "@CHECKOUTPUT Ran"',
  "@CHECKOUTPUTLINE": 'echo "@CHECKOUTPUTLINE Ran"',
  "@CHECKPACKAGE": 'echo "@CHECKPACKAGE Ran"'
}

complexfunctions = {}

argfunctions = ["@CHECKFORFILE"]

def compile_script(file):
    temp_file_path = tempfile.mkstemp()[1]
    new_file = open(temp_file_path, "w")

    file_list = file.read().splitlines()
    while "" in file_list:
        file_list.remove("")

    for line in file_list:
        line_list = line.split()
        if line_list[0] in simplefunctions.keys():
          if line_list[0] in argfunctions:
              new_file.write(f"{simplefunctions[line_list[0]].strip()} {line_list[1]}\n")
          else:
            new_file.write(f"{simplefunctions[line_list[0]].strip()}\n")
        else:
            new_file.write(line + "\n")

    subprocess.Popen(["bash", temp_file_path])

compile_script(open("test"))
