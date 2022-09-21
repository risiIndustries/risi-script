elements = [
    "TITLE",
    "DESCRIPTION",
    "ENTRY",
    "FILE",
    "DIRECTORY",
    "CHOICE",
    "BOOLEAN",
    "WARNING"
]

non_interactive_elements = [
    "TITLE",
    "DESCRIPTION",
    "WARNING"
]

test_code = """#!/bin/risi_script
#!/bin/risi_script
metadata:
  risiscript_version: 2.0
  name: "ScriptName"
  id: "com.example.scriptname"
  description: "Description of what the script does"
  dependencies: # Just put None for no dependencies
    - package1
    - package2
  tags: [root, reboot]


action: # Requires remove function
  show: |  # Only shows if the exit code is 0
    echo "Hello World"
    exit 0
  elements:
    entry_var:
      - ENTRY # Type of init var...
      - "Please enter something" # Question for user
    file_var:
      - FILE
      - "Please select a file" # Question for user
      - ".txt" # ex: *.txt. Use * for any type of file
    directory_var:
      - DIRECTORY
      - "Please select a directory"  # Question for user
    choice_var:
      - CHOICE
      - "Please choose this" # Question for users
      - [ "Choice1", "Choice2" ] # The choices for a user to pick
    boolean_var:
      - BOOLEAN
      - "Toggle this"
      - True
    warning:
      - WARNING
      - "Warning"
      - "This is a warning description"
  run: |
    echo "hello world"
  checks: | # Check if it runs
    ""
"""