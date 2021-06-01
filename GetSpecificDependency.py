from types import CodeType
from AR.ARHelpers import Module, PyFile

import sys
import json

#Where to dump the files information
files_dump = sys.argv[1]
#Where to dump the modules information
modules_dump = sys.argv[2]

from_module = sys.argv[3].upper()
to_module = sys.argv[4].upper()
project_folder = sys.argv[5]
files = {}
modules = {}

####################
#  helper methods  #
####################
def ends_with_py(file):
    return file[len(file)-3:].upper() == ".PY"

####################
#  Read the dumps  #
####################
JFiles = {}
JModules = {}
with open(files_dump, 'r') as fd:
    JFiles = json.load(fd)
with open(modules_dump, 'r') as md:
    JModules = json.load(md)

#Instantiate the data as objects
for jf in JFiles:
    name = JFiles[jf]["Name"]
    code = JFiles[jf]["Code"]
    comments = JFiles[jf]["Comments"]
    empty = JFiles[jf]["Empty"]
    imports = JFiles[jf]["Imports"]
    files[jf] = PyFile(name, code, comments, empty, imports)
for jm in JModules:
    name = JModules[jm]["Name"]
    mContains = []
    for c in JModules[jm]["Contains"]:
        mContains.append(files[c["Name"]])
    modules[jm] = Module(name, mContains, {})


for m in modules:
    if m.upper()[:len(from_module)] == from_module:
        for f in modules[m].Contains:
            for i in files[f.Name].Imports:
                if i.upper()[:len(to_module)] == to_module:
                    print("module:", m)
                    print("depends on:", i)