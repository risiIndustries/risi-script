from os import path
import sys

# Code didn't work so I made it work
if sys.argv[1] == "CHECKFORFILE":
  print(str(path.exists(sys.argv[2])).lower())
