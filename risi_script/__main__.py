import risi_script
import sys
import argparse

if __name__ == "__main__":
    if sys.argv[1] == "run": # Command syntax "risi-script file action args"
        with open(sys.argv[2], "r") as script_file:
            script = risi_script.Script(script_file)
            interactive_elements = sys.argv[4:]
            script.run_code(sys.argv[3], interactive_elements=interactive_elements)

    if sys.argv[1] == "get_actions":
        with open(sys.argv[2], "r") as script_file:
            script = risi_script.Script(script_file)
            print(script.get_actions())

    if sys.argv[1] == "get_available_actions":
        with open(sys.argv[2], "r") as script_file:
            script = risi_script.Script(script_file)
            print(script.get_available_actions())