# DependencyRecovery
Python script to help with architectural recovery. 

To run, replace the  "ZEEGUU_FOLDER1" on line 13 of main.py, with the path to the project to be analyzed.
Replace "level_to_draw" on line 249 with the desired level of abstraction. Abstraction level = depth of folder structure.

The analyze algorithms are horrible slow, so results can be saved as JSON by commenting and out-commenting the code in lines 176 - 207. Just replace the paths at line 14 and 15 to the desired location of the JSON dumps.