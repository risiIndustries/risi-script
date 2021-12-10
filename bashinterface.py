import os
import sys

if sys.argv[0] == "CHECKFORFILE":
    print(str(os.exists(sys.argv[1])).lower())
