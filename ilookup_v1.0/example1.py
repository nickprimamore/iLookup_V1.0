#!/usr/bin/env python3
from datetime import datetime  
myFile = open('append.txt', 'a')  
myFile.write('\nAccessed on ' + str(datetime.now()))  
