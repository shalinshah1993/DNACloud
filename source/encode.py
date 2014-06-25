"""
#########################################################################
Author: Shalin Shah, Vijay Dhameliya
Project: DNA Cloud
Graduate Mentor: Dixita Limbachya
Mentor: Prof. Manish K Gupta
Date: 5 November 2013
Website: www.guptalab.org/dnacloud
This module contains method to encode a given data file into corrosponding dnac file.
#########################################################################
"""

from cStringIO import StringIO
import sqlite3
import sqlite3 as lite
import unicodedata
import time
import csv
import sys
import HuffmanDictionary
import wx
#import psutil
import thread
import os
import gc
import extraModules

FILE_EXT = '.dnac'
if hasattr(sys, "frozen"):
        PATH = os.path.dirname(sys.executable)
else:
        PATH = os.path.dirname(os.path.abspath(__file__))
#print PATH , "encode"

def encode( readPath, savePath ):
        con = sqlite3.connect(PATH + '/../database/prefs.db')
        with con:
                cur = con.cursor()
                WORKSPACE_PATH = cur.execute('SELECT * FROM prefs WHERE id = 8').fetchone()[1]
                #print WORKSPACE_PATH
                if "linux" in sys.platform or 'darwin' in sys.platform:
                        WORKSPACE_PATH = unicodedata.normalize('NFKD', WORKSPACE_PATH).encode('ascii','ignore')
        
                if not os.path.isdir(WORKSPACE_PATH + '/.temp'):
                        os.mkdir(WORKSPACE_PATH +  '/.temp')
		
	genDNAString(readPath,WORKSPACE_PATH)
	genDNAChunks(readPath,savePath,WORKSPACE_PATH)
		
		
def genDNAString(readPath,WORKSPACE_PATH):
         try:                      
		fileOpened = open(readPath,"rb")
		seperator = ""
		if "win" in sys.platform and not 'darwin' in sys.platform:
			dnaFile = file(WORKSPACE_PATH + '\.temp\dnaString.txt','wb')
			seperator = "\\"
		elif "linux" in sys.platform or 'darwin' in sys.platform:
			dnaFile = file(WORKSPACE_PATH + '/.temp/dnaString.txt','wb')
			seperator = "/"
		
		file_type = ""
		ext_type = ""
		mtemp1 = readPath.split(seperator)
		file_name = mtemp1[len(mtemp1)-1]
		mtemp2 = file_name.split(".")
		if(len(mtemp2) == 3):
			file_type = mtemp2[len(mtemp2)-2]
			ext_type = mtemp2[len(mtemp2)-1]
		else:
			file_type = mtemp2[len(mtemp2)-1]

		del mtemp1
		del mtemp2
		del seperator
		# print file_type
		# print ext_type

		dnaLength = 0
		fileSize = os.path.getsize(readPath)
		fileOpened.seek(0,0)
		CHUNK_SIZE = 10000000
		if (fileSize % CHUNK_SIZE) == 0:
			if (fileSize/CHUNK_SIZE) == 0:
				noOfFileChunks = 1
			else:
				noOfFileChunks = (fileSize/CHUNK_SIZE)
		else:
			noOfFileChunks = (fileSize/CHUNK_SIZE) + 1 
		#print noOfFileChunks
		
		if noOfFileChunks > 1:
                        #print "Chunk No: 1",
                        tempString = StringIO()
			tempString.write(fileOpened.read(CHUNK_SIZE))
			a = extraModules.stringToAscii(tempString.getvalue())
			huffmanDictionary = HuffmanDictionary.stringToBase3(a)
			S1 = extraModules.HuffmanToString(huffmanDictionary)
			dnaString = extraModules.base3ToDNABase(S1)
			dnaFile.write(dnaString)
			dnaLength = dnaLength + len(S1)
			#fileOpened.flush()
			temp = dnaString[-1]
			
			del tempString
			del S1
			del a
			del huffmanDictionary
			
			for chunk_number in range(1,noOfFileChunks-1):
				#print "Chunk No:",chunk_number + 1
                                tempString = StringIO()
				tempString.write(fileOpened.read(CHUNK_SIZE))
					
				a = extraModules.stringToAscii(tempString.getvalue())
				huffmanDictionary = HuffmanDictionary.stringToBase3(a)
				S1 = extraModules.HuffmanToString(huffmanDictionary)
				dnaString = extraModules.base3ToDNABaseWithChar(S1,temp)
				dnaFile.write(dnaString)
				dnaLength = dnaLength + len(S1)
				dnaFile.flush()
				#fileOpened.flush()
				temp = dnaString[-1]

				del S1
				del huffmanDictionary
				del a
				del tempString
				
			#print "Chunk No:",noOfFileChunks
			
			tempString =StringIO()
			tempString.write(fileOpened.read(CHUNK_SIZE))
			a = extraModules.stringToAscii(tempString.getvalue())
			huffmanDictionary = HuffmanDictionary.stringToBase3(a)
			S1 = extraModules.HuffmanToString(huffmanDictionary)
			dnaString = extraModules.base3ToDNABaseWithChar(S1,temp)
			dnaFile.write(dnaString)
			dnaLength = dnaLength + len(S1)
			dnaFile.flush()
			#fileOpened.flush()
			
			del S1
			del huffmanDictionary
			del a
			del tempString
		else:
			#print "Chunk No: 1",
			tempString = StringIO()
			tempString.write(fileOpened.read())
			a = extraModules.stringToAscii(tempString.getvalue())
			huffmanDictionary = HuffmanDictionary.stringToBase3(a)
			S1 = extraModules.HuffmanToString(huffmanDictionary)
			dnaString = extraModules.base3ToDNABase(S1)
			dnaFile.write(dnaString)
			dnaLength = dnaLength + len(S1)
			#fileOpened.flush()
			
			del tempString
			del S1
			del a
			del huffmanDictionary		
		fileOpened.close()
		gc.collect()
		length = extraModules.decimalToBase3(dnaLength)
		S2 = str(length)
		mtemp = HuffmanDictionary.stringToBase3(extraModules.stringToAscii(","))
		mfile_type_temp = HuffmanDictionary.stringToBase3(extraModules.stringToAscii(file_type))
		mext_type_temp = HuffmanDictionary.stringToBase3(extraModules.stringToAscii(ext_type))
		mtemp1 = HuffmanDictionary.stringToBase3(extraModules.stringToAscii(":"))
		commaBase3 = ''.join(mtemp)
		colonBase3 = ''.join(mtemp1)
		mfile_type = ''.join(mfile_type_temp)
		mext_type = ''.join(mext_type_temp)
		length = dnaLength + len(S2) + len(commaBase3) + len(colonBase3) + len(mfile_type) + len(mext_type) + len(colonBase3)
		temp = length
		sx = ""
		while temp % 25 != 0:
			sx = sx + "0"
			temp = temp + 1
		S3 = sx
		S4 =  commaBase3 + mfile_type + colonBase3 + mext_type + colonBase3 + S3 + S2
		# print S4
		dnaFile.write(extraModules.base3ToDNABaseWithChar(S4,dnaString[-1]))
		dnaFile.flush()
		dnaFile.close()
	 except MemoryError:
		return -1

def genDNAChunks(readPath,path,WORKSPACE_PATH):
	try:
		if "." in readPath:
			temp = readPath.split( "." )
			readFileExtension = "." + temp[ len( temp ) - 1 ]
		else:
			readFileExtension = "" 
		
		if "win" in sys.platform and not 'darwin' in sys.platform:
			fileOpened = open( WORKSPACE_PATH + '\.temp\dnaString.txt', "rb" )
			fileSize = os.path.getsize(WORKSPACE_PATH + '\.temp\dnaString.txt' )
		elif "linux" in sys.platform or 'darwin' in sys.platform:
			fileOpened = open( WORKSPACE_PATH + '/.temp/dnaString.txt',"rb" )
			fileSize = os.path.getsize( WORKSPACE_PATH + '/.temp/dnaString.txt' )
		dnaFile = file( path + readFileExtension + FILE_EXT, 'wb' )
		
		dnaListLength = 0
		
		CHUNK_SIZE = 10000000
		if (fileSize % CHUNK_SIZE) == 0:
			if (fileSize/CHUNK_SIZE) == 0:
				noOfFileChunks = 1
			else:
				noOfFileChunks = (fileSize/CHUNK_SIZE)
		else:
			noOfFileChunks = (fileSize/CHUNK_SIZE) + 1 
		#print "No of Chunks :-",noOfFileChunks
		
		if noOfFileChunks > 1:
                        #print "Chunk No: 1"
			tempString = StringIO()
			tempString.write(fileOpened.read(CHUNK_SIZE))
			prependString = ""
			dnaString = tempString.getvalue()
		
			dnaList = extraModules.xstringToChunks(dnaString)
			dnaListLength = dnaListLength + len(dnaList)
			dnaList = str(dnaList)
			dnaFile.write(dnaList[1:-1])
			dnaFile.write(",")
			prependString = dnaString[-75:]
				
			#fileOpened.flush()
			dnaFile.flush()

			#print len(dnaString)/25 - 3 , len(dnaList)
			del tempString
			del dnaString
			del dnaList	
		
			for chunk_number in range(1,noOfFileChunks-1):
				#print "Chunk No:",chunk_number + 1
				tempString = StringIO()
				tempString.write(prependString)
				tempString.write(fileOpened.read(CHUNK_SIZE))
				prependString = ""
				dnaString = tempString.getvalue()
				dnaList = extraModules.xstringToChunks(dnaString)
				dnaListLength = dnaListLength + len(dnaList)
				dnaList = str(dnaList)
				dnaFile.write(dnaList[1:-1])
				dnaFile.write(",")
				prependString = dnaString[-75:]
				
				#fileOpened.flush()
				dnaFile.flush()

				del tempString
				del dnaString
				del dnaList
		
			#print "Chunk No:",noOfFileChunks
			tempString = StringIO()
			tempString.write(prependString)
			tempString.write(fileOpened.read())
			dnaString = tempString.getvalue()
			dnaList = extraModules.xstringToChunks(dnaString)
			dnaListLength = dnaListLength + len(dnaList)
			dnaList = str(dnaList)
			dnaFile.write(dnaList[1:-1])
			dnaFile.write(",")
			
			#fileOpened.flush()
			dnaFile.flush()

			del prependString
			del tempString
			del dnaString
			del dnaList
		else:
			#print "Chunk No: 1"
			tempString = StringIO()
			tempString.write(fileOpened.read())
			prependString = ""
			dnaString = tempString.getvalue()
		
			dnaList = extraModules.xstringToChunks(dnaString)
			dnaListLength = dnaListLength + len(dnaList)
			dnaList = str(dnaList)
			dnaFile.write(dnaList[1:-1])
			dnaFile.write(",")
				
			#fileOpened.flush()
			dnaFile.flush()
				
			del tempString
			del dnaString
			del dnaList	
		#print dnaListLength , "List"
		gc.collect()
		fileOpened.close()  
		dnaFile.close()
		
		return
	except MemoryError:
		return -1
