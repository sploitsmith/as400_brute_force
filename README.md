//Updated the as400 code from https://github.com/milo2012/pentest_scripts/tree/master/as400

The following changes were made:
1. Target port was hard-coded to 993 in session.py (line 13)
2. Variable 'idx' was used but not defined in vt5250.py (lines 303 and 304)
3. Userlist was hard-coded in testAS400.py (line 78). It now reads in a file
4. Added a user-pass file (modified from http://www.vulnerabilityassessment.co.uk/as400_users.txt)

The tool can be run with the command
testAS400.py -i [IP address] -p [port number]

Additional users can be added to the file "as400_users.txt"
