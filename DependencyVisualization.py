from AR.ARHelpers import Module, PyFile

import sys
import json
from pyvis.network import Network

#Where to dump the files information
files_dump = sys.argv[1]
#Where to dump the modules information
modules_dump = sys.argv[2]
#What depth of module to look at
level_to_draw = int(sys.argv[3])
files = {}
modules = {}

####################
#  helper methods  #
####################
def module_from_level(module, level):
    mod = modules[module]
    levels = mod.Name.split('.')
    #If the module is below the level, but only contains 1 file/the module is the file
    # then it should be counted on all subsequent levels, otherwise data is lost
    if mod.MLevel < level:
        if len(modules[module].Contains) == 1:
            return module
        else:
            return None
    return ('.').join(levels[:level+1])



####################
#  Read the dumps  #
####################
JFiles = {}
with open(files_dump, 'r') as fd:
    JFiles = json.load(fd)
JModules = {}
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

max_depth_of_modules = max(i.MLevel for i in modules.values())

for level in range(max_depth_of_modules+1):
    for m in modules:
        mod = modules[m]
        if mod.MLevel == level:
            modFiles = mod.Contains
            for f in modFiles:
                for i in f.Imports:
                    modRef = module_from_level(i, level)
                    if modRef:
                        #if the import in the dictionary increment it, else add it
                        try:
                            mod.DependsOn[modRef] = mod.DependsOn[modRef] + 1 
                        except:
                            mod.DependsOn[modRef] = 1
                    else:
                        continue

################
# Draw a graph #
################

#Wanted to make it a spectrum between green and red depending on the ratio between
# lines of comments and code, just to make it more interesting to look at but running out of time
def Color_of_node(module):
    mod = modules[module]
    lines_of_code = sum([file.Code for file in mod.Contains])
    if lines_of_code == 0:
        return "gray"
    lines_of_comments = sum([file.Comments for file in mod.Contains])
    if lines_of_comments == 0:
        return "red"
    ratio = lines_of_comments/lines_of_code
    if ratio > 0.1:
        return "green"
    if ratio > 0.05:
        return "yellow"
    return "red"

modules_to_draw = []
for m in modules:
    if modules[m].MLevel == level_to_draw:
        modules_to_draw.append(m)

net = Network(directed=True)

#add nodes
for m in modules_to_draw:
    size = sum([file.Code for file in modules[m].Contains])
    net.add_node(m, label=m, value=size, title=str(size), shape="square", color=Color_of_node(m))

#add edges
for m in modules_to_draw:
    modules_edges = modules[m].DependsOn
    for edge in modules_edges:
        if edge != m:
            net.add_edge(m, edge, width=(modules_edges[edge]/20), arrowStrikethrough=False, label=modules_edges[edge], color="Black")

net.set_edge_smooth("horizontal")
net.show("test.html")
