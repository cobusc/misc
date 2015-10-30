README
======

Requirements
------------
This application requires Python to be installed. It was tested using Python 2.7.10, but should work with versions 2.7 and higher (3.x).

Usage
-----
The application can be run directly in a Linux environment
```bash
./calculate_fleet_summary.py
```
or
```bash
python calculate_fleet_summary.py
```

As per the instructions it will read a file called "FleetState.txt". This file needs to be present in the current working directory. On success, a file called "Statistics.txt" will be created -- also in the current working directory.

On success, the application will exit with an exit code of `0` (zero). If an error occurred, some information regarding the error will be displayed and a non-zero exit code will be returned. For example, running the application when there is no input file available...
```bash
./calculate_fleet_summary.py
```
...results in the following output:
```
[Errno 2] No such file or directory: 'FleetState.txt'
```
Inspecting the exit code...
```bash
echo $?
```
...yields:
```
1
```

Input validation failures
-------------------------

When the application encounters an input validation error, it will return with a non-zero exit code and output detailing the line on which the error occurred and what the error was. For example:
```
Line 12: Host ID '79' specified more than once.
```
or
```
Line 4: Unknown instance type 'M5'
```

Corner cases
------------
When all slots for an instance type are filled, applying the "most filled" definition will not return any results. I have chosen to handle this case by setting `(host_count, empty_slots)` to `(0, 0)` in the output file. This will never overlap with results produced in the general case (because `empty_slots=0` is not allowed).

### Example
Given the input file...
```
0,M1,1,1
```
..the following output will be generated:
```
EMPTY: M1=0;
FULL: M1=1;
MOST_FILLED: M1=0,0;
```

Tests
-----
Run `./tests.py` or `python tests.py`.


Why Python?
-----------
I chose Python as it is the language I currently use for development. Python is an expressive language, meaning it allows a developer to write easily understandable code, without the need for much boilerplating.

Python does have the drawback that it is sometimes slower than other (usually compiled) languages and one needs to take this into consideration when building computationally intensive applications.

References
----------
See `instructions.txt` for the original instructions.
