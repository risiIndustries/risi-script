import yaml
import tempfile
import os
import subprocess

# Input functions
simplefunctions = {}

simplefunctions["@INPUT"] = """
echo "@INPUT Ran"
"""
simplefunctions["@FILE"] = """
echo "@FILE Ran"
"""
simplefunctions["@DIRECTORY"] = """
echo "@DIRECTORY Ran"
"""
simplefunctions["@CHOICE"] = """
echo "@CHOICE Ran"
"""

# Need a way to get the input and raise an error if no input is found.
simplefunctions["@CHECKFORFILE"] = """
python3 bashinterface.py CHECKFORFILE
"""
simplefunctions["@CHECKINFILE"] = """
echo "@CHECKINFILE Ran"
"""
simplefunctions["@CHECKOUTPUT"] = """
echo "@CHECKOUTPUT Ran"
"""
simplefunctions["@CHECKOUTPUTLINE"] = """
echo "@CHECKOUTPUTLINE Ran"
"""
simplefunctions["@CHECKPACKAGE"] = """
echo "@CHECKPACKAGE Ran"
"""

complexfunctions = {}

def compile_script(file):
    temp_file_path = tempfile.mkstemp()[1]
    new_file = open(temp_file_path, "w")

    file_list = file.read().splitlines()
    while "" in file_list:
        file_list.remove("")

    for line in file_list:
        line_list = line.split()
        if line_list[0] in simplefunctions.keys():
            new_file.write(simplefunctions[line_list[0]].strip() + "\n")
        else:
            new_file.write(line + "\n")

def parse(code):
    pass # Added pass so code doesn't error.
