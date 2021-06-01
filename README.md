# DependencyRecovery
Python script to help with architectural recovery. 
So far only works on python projects.

## DependencyRecovery
The scripts runs through every .py file in the project and saves their dependencies as JSON files.
The script takes three arguments. First being the root folder of the project thhe analyze. Second being where to save the files information. Last is where to save the modules information.
python DependencyRecovery.py PathToProject PathToFilesDump PathToModulesDump  

## DependencyVisualization
The script visualizes the data gathered from DependencyRecovery.
The script takes three arguments. First being the path the the files information. Second being the path to the modules information. Third is the level of abstraction (This is very janky and keeping it at 0 is adviced)
python DependencyVisualization.py PathToFilesDump PathToModulesDump Level
