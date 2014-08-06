"""
#########################################################################
Author: Vijay Dhameliya, Madhav Khakhar
Project: DNA Cloud
Graduate Mentor: Dixita Limbachya
Mentor: Prof. Manish K Gupta
Date: 28 July 2013
Website: www.guptalab.org/dnacloud
This file contains implementation of various compression techniques.
#########################################################################
"""

from cStringIO import StringIO
import sqlite3
import sqlite3 as lite
from sqlite3 import OperationalError
import unicodedata
import time
import csv
import sys
import GolayDictionary
import wx
#import psutil
import thread
import os
import gc
import extraModules

if hasattr(sys, "frozen"):
        PATH = os.path.dirname(sys.executable)
else:
        PATH = os.path.dirname(os.path.abspath(__file__))


def decode( readPath, savePath ):
	con = sqlite3.connect(PATH + '/../database/prefs.db')
        with con:
                cur = con.cursor()
                WORKSPACE_PATH = cur.execute('SELECT * FROM prefs WHERE id = 8').fetchone()[1]
                if "linux" in sys.platform:
                        WORKSPACE_PATH = unicodedata.normalize('NFKD', WORKSPACE_PATH).encode('ascii','ignore')
                if not os.path.isdir(WORKSPACE_PATH + '/.temp'):
                        os.mkdir(WORKSPACE_PATH +  '/.temp')
                        
	if "win" in sys.platform and not 'darwin' in sys.platform:
		tempFilePath = WORKSPACE_PATH + '\dnaString.txt'
	elif "linux" in sys.platform or 'darwin' in sys.platform:
		tempFilePath = WORKSPACE_PATH + '/dnaString.txt'
		
	degenerateDNAChunksInOrder(readPath,tempFilePath)
	degenerateDNAString(readPath,tempFilePath,savePath)


def degenerateDNAChunksInOrder(readPath,tempPath):
	fileOpened = open(readPath,"rb")
	dnaStringFile = open(tempPath,"wb")

	fileSize = os.path.getsize(readPath)
	CHUNK_SIZE = 10000000
	if (fileSize % CHUNK_SIZE) == 0:
		if (fileSize/CHUNK_SIZE) == 0:
			noOfFileChunks = 1
		else:
			noOfFileChunks = (fileSize/CHUNK_SIZE)
	else:
		noOfFileChunks = (fileSize/CHUNK_SIZE) + 1

	if noOfFileChunks > 1:
		prependString = ""
		for chunk_number in xrange(0,noOfFileChunks):
			dnaList = fileOpened.read(CHUNK_SIZE)
			tempString = prependString
			prependString = ""
			j = -1
			while True:
				if dnaList[j] == '\n':
					break
				prependString = dnaList[j] + prependString
				j -= 1
			tempList = (tempString + dnaList[:j]).split("\n")
			dnaString = StringIO()
			for i in xrange(len(tempList)):
				if tempList[i][0] != " ":
					dnaString.write(tempList[i][0:99])
				else:
					dnaString.write(tempList[i][2:101])
			dnaStringFile.write(dnaString.getvalue())
			dnaStringFile.flush()

			del tempList
			del dnaString
			del j
			del dnaList
			del tempString

	else:
		dnaList = fileOpened.read()
		prependString = ""
		j = -1
		while True:
			if dnaList[j] == '\n':
				break
			prependString = dnaList[j] + prependString
			j -= 1
		tempList = dnaList[:j].split("\n")
		dnaString = StringIO()
		for i in xrange(len(tempList)):
			dnaString.write(tempList[i][0:99])
		dnaStringFile.write(dnaString.getvalue())
		dnaStringFile.flush()

		del tempList
		del dnaString
		del j
		del dnaList

		fileOpened.close()
		dnaStringFile.close()

def degenerateDNAChunks(readPath,tempPath):
	fileOpened = open(readPath,"rb")
	dnaStringFile = open(tempPath,"wb")

	conn = sqlite3.connect(PATH + '/../database/test.db')
	cur = conn.cursor()
	try:
		cur.execute('''CREATE TABLE CHUNKS
	       (CHUNKINDEX INT PRIMARY KEY     NOT NULL,
	        CHUNKVALUE TEXT    NOT NULL);''')
		conn.commit()
	except OperationalError:
		None


	fileSize = os.path.getsize(readPath)
	CHUNK_SIZE = 10000000

	if (fileSize % CHUNK_SIZE) == 0:
		if (fileSize/CHUNK_SIZE) == 0:
			noOfFileChunks = 1
		else:
			noOfFileChunks = (fileSize/CHUNK_SIZE)
	else:
		noOfFileChunks = (fileSize/CHUNK_SIZE) + 1

	if noOfFileChunks > 1:
		prependString = ""
		for chunk_number in xrange(0,noOfFileChunks):
			dnaList = fileOpened.read(CHUNK_SIZE)
			tempString = prependString
			prependString = ""
			j = -1
			while True:
				if dnaList[j] == '\n':
					break
				prependString = dnaList[j] + prependString
				j -= 1
			tempList = (tempString + dnaList[:j]).split("\n")
			dnaString1 = StringIO()
			for i in xrange(len(tempList)):
				dnaString1.write(tempList[i][0:99])
				dnaString = tempList[i][0:99]
				lastChar = dnaString[-1]
				chunkIndexDNA = tempList[i][99:-3]
				chunkIndexbase3 = extraModules.DNABaseToBase3WithChar(chunkIndexDNA,lastChar)
				chunkIndex = extraModules.base3ToDecimal(chunkIndexbase3)
				conn.execute("INSERT INTO CHUNKS (CHUNKINDEX,CHUNKVALUE) \
			      VALUES (?, ?);", (chunkIndex, dnaString))
				conn.commit()

			# dnaStringFile.write(dnaString1.getvalue())
			# dnaStringFile.flush()

			del tempList
			del dnaString
			del j
			del dnaList
			del tempString

	else:
		dnaList = fileOpened.read()
		prependString = ""
		j = -1
		while True:
			if dnaList[j] == '\n':
				break
			prependString = dnaList[j] + prependString
			j -= 1
		tempList = dnaList[:j].split("\n")
		dnaString1 = StringIO()
		for i in xrange(len(tempList)):
			dnaString1.write(tempList[i][0:99])
			dnaString = tempList[i][0:99]
			lastChar = dnaString[-1]
			chunkIndexDNA = tempList[i][99:-3] 
			chunkIndexbase3 = extraModules.DNABaseToBase3WithChar(chunkIndexDNA,lastChar)
			chunkIndex = extraModules.base3ToDecimal(chunkIndexbase3)
			conn.execute("INSERT INTO CHUNKS (CHUNKINDEX,CHUNKVALUE) \
				VALUES (?, ?);", (chunkIndex, dnaString))
			conn.commit()

		# dnaStringFile.write(dnaString1.getvalue())
		# dnaStringFile.flush()

		del tempList
		del dnaString
		del j
		del dnaList

	cursor = conn.execute("SELECT chunkindex, chunkvalue  from CHUNKS order by chunkIndex asc")
	dnaString = StringIO()
	for row in cursor:
		dnaString.write(row[1])

	dnaStringFile.write(dnaString.getvalue())
	dnaStringFile.flush()
	conn.execute("DELETE from CHUNKS;")
	conn.commit()

	conn.close()

	fileOpened.close()
	dnaStringFile.close()

def degenerateDNAString(readPath,tempPath,savePath):
	dnaFile = open(tempPath,"rb")
	fileSize = os.path.getsize(tempPath)
	dnaFile.seek(0,0)

	i=100
	dnaFile.seek(fileSize - 100,0)
	mtemp = dnaFile.read()
	base3String = extraModules.DNABaseToBase3WithChar(mtemp[1:100],mtemp[0])
	asciiList = GolayDictionary.base3ToAsciiWithoutError(base3String)
	resString  = extraModules.asciiToString(asciiList)

	while ',' not in resString:
			i=i+99
			if(fileSize > i):
				dnaFile.seek(fileSize - i,0)
				mtemp = dnaFile.read()
				base3String = extraModules.DNABaseToBase3WithChar(mtemp[1:i],mtemp[0])
				asciiList = GolayDictionary.base3ToAsciiWithoutError(base3String)
				resString  = extraModules.asciiToString(asciiList)
			else:
				dnaFile.seek(0,0)
				mtemp = dnaFile.read()
				base3String = extraModules.DNABaseToBase3(mtemp)
				asciiList = GolayDictionary.base3ToAsciiWithoutError(base3String)
				resString  = extraModules.asciiToString(asciiList)
				break;
	
	mtemp = resString.split(",")
	fileTail = mtemp[len(mtemp)-1]
	mtemp = fileTail.split(":")
	file_type = mtemp[0]
	file_size = str(mtemp[1])
	if "\0" in file_size:
		mtemp = file_size.split("\0")
		fileSize = int(mtemp[len(mtemp)-1])
	else:
		fileSize = int(file_size)

	saveFile = savePath+ "." + file_type
	decodedFile = file( saveFile ,'wb')


	CHUNK_SIZE = 9900000
	if (fileSize % CHUNK_SIZE) == 0:
		if (fileSize/CHUNK_SIZE) == 0:
			noOfFileChunks = 1
		else:
			noOfFileChunks = (fileSize/CHUNK_SIZE)
	else:
		noOfFileChunks = (fileSize/CHUNK_SIZE) + 1

	dnaFile.seek(0,0)

	if noOfFileChunks > 1:
		tempString = StringIO()
		tempString.write(dnaFile.read(CHUNK_SIZE))
		dnaString = tempString.getvalue()
		prevChar = dnaString[-1]
		base3String = extraModules.DNABaseToBase3(dnaString)
		asciiList = GolayDictionary.base3ToAscii(base3String, dnaString, '0')
		resString  = extraModules.asciiToString(asciiList)
		decodedFile.write(resString)
		decodedFile.flush()

		del tempString
		del asciiList
		del resString

		for chunk_number in range(1,noOfFileChunks-1):
			tempString = StringIO()
			tempString.write(dnaFile.read(CHUNK_SIZE))
			dnaString = tempString.getvalue()
			base3String = extraModules.DNABaseToBase3WithChar(dnaString,prevChar)
			asciiList = GolayDictionary.base3ToAscii(base3String,dnaString,prevChar)
			prevChar = dnaString[-1]
			resString  = extraModules.asciiToString(asciiList)
			decodedFile.write(resString)
			decodedFile.flush()

			del tempString
			del asciiList
			del resString

		tempString = StringIO()
		tempString.write(dnaFile.read(fileSize - (noOfFileChunks - 1) * CHUNK_SIZE))
		dnaString = tempString.getvalue()
		base3String = extraModules.DNABaseToBase3WithChar(dnaString,prevChar)
		asciiList = GolayDictionary.base3ToAscii(base3String,dnaString,prevChar)
		prevChar = dnaString[-1]
		resString  = extraModules.asciiToString(asciiList)
		decodedFile.write(resString)
		decodedFile.flush()

		del tempString
		del asciiList
		del resString

	else:
		tempString = StringIO()
		tempString.write(dnaFile.read(fileSize))
		dnaString = tempString.getvalue()
		prevChar = dnaString[-1]
		base3String = extraModules.DNABaseToBase3(dnaString)
		asciiList = GolayDictionary.base3ToAscii(base3String,dnaString,'0')
		resString  = extraModules.asciiToString(asciiList)
		decodedFile.write(resString)
		decodedFile.flush()

		del tempString
		del asciiList
		del resString

	dnaFile.close()
	decodedFile.close()