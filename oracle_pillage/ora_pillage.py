import cx_Oracle
import time
import sys
import csv
import re
import argparse
import urllib
import os.path
import fileinput
import subprocess
import socket
import os
import itertools
from collections import defaultdict
from pprint import pprint
from termcolor import colored

#http://hivelocity.dl.sourceforge.net/project/cx-oracle/5.1.1/cx_Oracle-5.1.1.tar.gz
outputFileCSV=""
ccRegex = []
ccRegex.append("^4[0-9]{12}(?:[0-9]{3})?$")		#Visa Regex	
ccRegex.append("^5[1-5][0-9]{14}$")			#Mastercard Regex
ccRegex.append("^3[47][0-9]{13}$")			#Amex Regex
ccRegex.append("^3(?:0[0-5]|[68][0-9])[0-9]{11}$")	#Diners Regex
ccRegex.append("^6(?:011|5[0-9]{2})[0-9]{12}$")		#Discover Regex		
ccRegex.append("^(?:2131|1800|35\d{3})\d{11}$")		#JCDB Regex

def cardLuhnChecksumIsValid(card_number):
    """ checks to make sure that the card passes a luhn mod-10 checksum """

    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1

    for count in range(0, num_digits):
        digit = int(card_number[count])

        if not (( count & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit
    return ( (sum % 10) == 0 )
    
def dataExtract(username,password,hostname,sid):
	print "[+] Extracting data from database"
	try:
		orcl1 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)		
		curs = orcl1.cursor()	
		curs.execute("select * from v$database")
		for db_data in curs:
			#Iterate per database
			dbName = db_data[1]
			print "[+] Database found: "+dbName
			
			orcl2 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)		
			curs2 = orcl2.cursor()
			tblCount2 = curs2.execute("SELECT COUNT(*) FROM tab")	
			#Get a count of the total tables in the databases
			if tblCount2<1:
				print "There are no tables in "+dbName+". Its possible that the account does not have access. Try escalating privileges."
			if tblCount2:
				#Continue with CC data search	
				orcl3 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)		
				curs3 = orcl3.cursor()	
				curs3.execute("SELECT * FROM tab")	#Get a list of all tables
				for row_data in curs3:
					#Iterate per table 
					if not row_data[0].startswith('BIN$'): # skip recycle bin tables
						tableName = row_data[0]
						try:
							print colored("\n[+] Ransacking table: "+tableName+" in "+sid,"red",attrs=['bold'])
							orcl4 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)		
							sql4 = "select * from (select * from  " + tableName+") where rownum <=10"
							curs4 = orcl4.cursor()
							curs4.execute(sql4)
							matchedRows = []
							results = curs4.fetchall()
						except cx_Oracle.DatabaseError:
							continue
						except cx_Oracle.DatabaseError:
							continue
						
						global outputFileCSV
						if outputFileCSV!="":
							for result in results:
								print str(result)
								#Write all results to output file
								fo = open(outputFileCSV, "a+")
								fo.write(str(result)+"\n")
								fo.close()					
						else:
							for result in results:
								print result
						results = curs4.fetchall()
						for searchStr in ccRegex:
							#Credit Card Regex Search
							p = re.compile(searchStr)
							for row_data in results:
								for col in row_data:
									if p.match(str(col)):
										#Run the found CC info thru LUHN algorithm to confirm
										n = p.match(str(col))
										if cardLuhnChecksumIsValid(str(col)):
											print colored("[+] Found valid CC: %s in table %s [%s]" % (col, tableName, sid),"red",attrs=['bold'])
										else:
											print "%s is not valid credit card number" % col
										matchedRows.append(row_data)
						#Write rows that matched to csv file				
						if len(matchedRows) > 0:
							csv_file_dest = dbName +  '_' + tableName + ".csv"
							print colored("\n[+] Results for first ten rows have been saved to "+csv_file_dest+".","red",attrs=['bold'])
							outputFile = open(csv_file_dest,'w') 
							output = csv.writer(outputFile, dialect='excel')			
		
							#if printHeader: # add column headers if requested
							cols = []
							for col in curs4.description:
								cols.append(col[0])
							output.writerow(cols)
			
							for rows in matchedRows: # add table rows
								output.writerow(rows)	
							outputFile.close()
						curs4.close()
				curs3.close()
			curs2.close()	
		curs.close()		
	
	except cx_Oracle.DatabaseError as e:
		print e
		tableNames = []
		if "table or view does not exist" in str(e):
			#Display tables in current SID due to limited permissions
                        orcl2 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)
                        curs2 = orcl2.cursor()
                        curs2.execute("SELECT table_name FROM user_tables")
                        #curs2.execute("SELECT table_name FROM all_tab_columns WHERE column_name LIKE \'%%\'")
                        for row_data in curs2:
                        	#Iterate per table 
                                if not row_data[0].startswith('BIN$'): # skip recycle bin tables
                                	tableName = row_data[0]
					if tableName not in tableNames:
						tableNames.append(tableName)
			for tableName in tableNames:
				print str(tableName)
				try:
	                                print colored("\n[+] Ransacking table: "+tableName+" in "+sid,"red",attrs=['bold'])
        	                        orcl4 = cx_Oracle.connect(username+"/"+password+"@"+hostname+":1521/"+sid)
                	                sql4 = "select * from (select * from  " + tableName+") where rownum <=10"
                        	        curs4 = orcl4.cursor()
                                	curs4.execute(sql4)
	                                matchedRows = []
        	                        results = curs4.fetchall()
					for result in results:
						print str(result)
				except cx_Oracle.DatabaseError as e:
					if "table or view does not exist" in str(e):
						pass
			#for result in results:
			#	print str(result)
	#	print "cx_Oracle.DatabaseError"
	#	pass	
#outputFileCSV="output4.csv"	
username=""
password=""
hostname=""
sid=""
dataExtract(username,password,hostname,sid)
