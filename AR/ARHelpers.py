class Module:
    def __init__(self, name, contains, dependsOn):
        self.Name = name 
        #Module level
        self.MLevel = name.count('.')
        #The modules contained in this module
        self.Contains = contains
        #Outgoing dependencies from this module
        self.DependsOn = dependsOn

class PyFile:
    def __init__(self, name, code, comments, empty, imports):
        self.Name = name
        #number of lines of code
        self.Code = code
        #number of lines of comments
        self.Comments = comments
        #number of empty lines 
        self.Empty = empty 
        #List of imports in this file
        self.Imports = imports