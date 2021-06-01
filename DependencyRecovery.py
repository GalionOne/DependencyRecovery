from types import CodeType
from AR.ARHelpers import Module, PyFile

import sys
import re
import json
from os import path
from pathlib import Path

#Path to the project folder to be analyzed
Project_folder = sys.argv[1] 
#Where to dump the files information
files_dump = sys.argv[2]
#Where to dump the modules information
modules_dump = sys.argv[3]
files = {}
modules = {}
max_depth = 0

####################################
# Define methods for file analysis #
####################################
#Lines of code returns (lines with code, lines with comments, empty lines)
def LOC(file):
    code = 0
    comment = 0
    empty = 0
    for line in open(file):
        #Does the line only contain 0 or more whitespace characters
        if re.search("^\s*$", line):
            empty += 1
            continue
        #Does the line only contain 0 or more whitespace characters followed by a '#'
        if re.search("^\s*#", line):
            comment += 1
            continue
        #Otherwise it is probably a line of code
        code += 1
    return code, comment, empty

#Slightly naive way of retriving imports. It is assuming that only 0 or more whitespaces
# can be in front of an import. I do not know enough about python to know if other methods
# of importing exists
def Get_import_from_line(line):
    x = re.search("^(\s*import )(\S+)", line)
    if x:
        return(x.group(2))
    y = re.search("^(\s*from )(\S+)", line)
    if y:
        return(y.group(2))

#Needs the full path to the import gotten through something like Get_proper_import 
# maybe not ideal, but gets the job done  
def Is_path_from_project(imprt):
    #check if it's a file
    exists = path.exists(imprt + ".py")
    #check if it's a folder
    exists = exists or path.exists(imprt)
    return exists

def Is_Module_from_project(imprt):
    imprt_path = imprt.replace('.', '\\')
    py_path = imprt_path + ".py"
    dir_path = imprt_path
    for p in Path(Project_folder).rglob(py_path):
        return module_from_file_path(Project_folder, str(p))
    for p in Path(Project_folder).rglob(dir_path):
        return module_from_file_path(Project_folder, str(p))
    return None

#imports starting with '.' represents relative paths. 
#These has to be made into proper modules taking start from the base folder 
def Get_proper_import(file, imprt):
    file_path = file.split('\\')
    imprt_relative = imprt.split('.')
    #If the import is not beginning with '.'
    if imprt_relative[0] != '':
        file_path = Project_folder.split('\\')
    
    #if a relative path is '..' it len(imprt_relative) will be 3, but len(imprt) will be 2
    #which is the correct depth. I'm assuming import can't looke like '.somehting.'
    if len(imprt_relative) > len(imprt):
        imprt_relative_depth = len(imprt)
    else:
        imprt_relative_depth = sum(i == '' for i in imprt_relative)
    file_path = file_path[:len(file_path)-imprt_relative_depth]
    impt_path = imprt_relative[imprt_relative_depth:]
    tmp = Is_Module_from_project(str(impt_path))

    impt_path = ('\\').join(file_path + impt_path)
    #Hack to handle annoying python imports
    if impt_path[len(impt_path)-1] == '\\':
        impt_path = impt_path[:len(impt_path)-1]
    if Is_path_from_project(impt_path):
        return impt_path
    return imprt

#Transform path to module. god/help/us/all -> god.help.us.all 
def module_from_file_path(folder_prefix, full_path):
    file_name = full_path[len(folder_prefix):]
    file_name = file_name.replace("\\",".")
    file_name = file_name.replace(".py","")
    #[1:] to get rid of the initial '.'
    return file_name[1:]

def Imports(file):
    imports = []
    for line in open(file):
        i = Get_import_from_line(line)
        if i:
            i = Get_proper_import(file, i)
            #If the import was a relative path
            if i[:3] == Project_folder[:3]:
                i = module_from_file_path(Project_folder, i)
            #if it was a complete path, or external import
            else:
                i = Is_Module_from_project(i) 
                if i:
                    i.replace('.','\\')
                    i = Project_folder + '\\' + i
                    i = module_from_file_path(Project_folder, i)
                #out comment this else to add external modules to the list of imports
                else:
                    i = None
        if i and i not in imports:
            imports.append(i)
    return imports

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

#############################
# Analyse files and modules #
#############################
#Analyse all .py files
def Analyze_files():
    for file in Path(Project_folder).rglob("*.py"):
        name = str(file)
        (code, comment, empty) = LOC(name)
        imports = Imports(name)
        files[name] = PyFile(name, code, comment, empty, imports)

#Create the initial list of modules
def Analyze_modules():
    for file in files:
        name = module_from_file_path(Project_folder, file)
        #The level of a module is decided by how many '.' is in the module name
        module_levels = name.split('.')

        depth_of_module = len(module_levels) + 1
        #Starts at 1 to ignore the empty string
        for i in range(1, depth_of_module):
            m = '.'.join(module_levels[:i])
            #If a module is not already in the list, add it
            #This adds both the folders and .py files as modules
            if not any(mod == m for mod in modules):
                modules[m] = Module(m, [], {})

            modules[m].Contains.append(files[file])

Analyze_files()
Analyze_modules()

with open(files_dump, 'w') as fd:
    content = json.dumps(files, default=vars, indent=4)
    fd.write(content)
with open(modules_dump, 'w') as md:
    content = json.dumps(modules, default=vars, indent=4)
    md.write(content)