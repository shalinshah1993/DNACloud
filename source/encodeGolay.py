# -*- coding: utf-8 -*-
"""
#########################################################################
Author: Madhav Khakhar, Vijay Dhameliya
Project: DNA Cloud
Graduate Mentor: Dixita Limbachya
Mentor: Prof. Manish K Gupta
Date: 25 July 2014
Website: www.guptalab.org/dnacloud
This module contains encoding scheme which uses Golay Codes
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
import math


FILE_EXT = '.dnac'
chunkIndex = 0
noOfBits = 0
noOfChunks = 0
if hasattr(sys, "frozen"):
        PATH = os.path.dirname(sys.executable)
else:
        PATH = os.path.dirname(os.path.abspath(__file__))

def encode( readPath, tempPath, savePath ):
	
	if not os.path.isdir(tempPath + '/.temp'):
		os.mkdir(tempPath +  '/.temp')
	if "win" in sys.platform and not 'darwin' in sys.platform:
		tempFilePath = tempPath + '\.temp\dnaString.txt'
	elif "linux" in sys.platform or 'darwin' in sys.platform:
		tempFilePath = tempPath + '/.temp/dnaString.txt'
		
	generateDNAString(readPath,tempFilePath)
	generateDNAChunks(readPath,tempFilePath,savePath)



def generateDNAString(readPath,tempPath):
	xtemp = readPath.split(".")
	dnaStringFile = file(tempPath, 'wb')
	fileOpened = open(readPath,"rb")
	fileSize = os.path.getsize(readPath)
	
	global noOfBits
	global noOfChunks

	fileOpened.seek(0,0)

	CHUNK_SIZE = 10000000
	if (fileSize % CHUNK_SIZE) == 0:
		if (fileSize/CHUNK_SIZE) == 0:
			noOfFileChunks = 1
		else:
			noOfFileChunks = (fileSize/CHUNK_SIZE)
	else:
		noOfFileChunks = (fileSize/CHUNK_SIZE) + 1

	if noOfFileChunks > 1:
		tempString = StringIO()
		tempString.write(fileOpened.read(CHUNK_SIZE))
		fileInputString = tempString.getvalue()
		base3String = GolayDictionary.stringToBase3(extraModules.stringToAscii( fileInputString ))
		dnaString = extraModules.base3ToDNABase(base3String)
		prevChar = dnaString[len(dnaString)-1]
		dnaStringFile.write(dnaString)
		dnaStringFile.flush()

		del tempString
		del fileInputString
		del base3String

		for chunk_number in range(1,noOfFileChunks):
			tempString = StringIO()
			tempString.write(fileOpened.read(CHUNK_SIZE))
			fileInputString = tempString.getvalue()
			base3String = GolayDictionary.stringToBase3(extraModules.stringToAscii( fileInputString ))
			dnaString = extraModules.base3ToDNABaseWithChar(base3String,prevChar)
			prevChar = dnaString[len(dnaString)-1]
			dnaStringFile.write(dnaString)
			dnaStringFile.flush()

			del tempString
			del fileInputString
			del base3String

	else:
		tempString = StringIO()
		tempString.write(fileOpened.read())
		fileInputString = tempString.getvalue()
		base3String = GolayDictionary.stringToBase3(extraModules.stringToAscii( fileInputString ))
		dnaString = extraModules.base3ToDNABase(base3String)
		prevChar = dnaString[len(dnaString)-1]
		dnaStringFile.write(dnaString)
		dnaStringFile.flush()

		del tempString
		del fileInputString
		del base3String

	fileOpened.close()
	gc.collect()

	len_s1 = fileSize * 11
	
	commaBase3 = GolayDictionary.stringToBase3( extraModules.stringToAscii(",") )
	colonBase3 = GolayDictionary.stringToBase3( extraModules.stringToAscii(":") )
	file_ext = GolayDictionary.stringToBase3( extraModules.stringToAscii( xtemp[len(xtemp) - 1] ) )
	s3 = GolayDictionary.stringToBase3(extraModules.stringToAscii( str(len_s1)) )
	s4 = len_s1 + len(commaBase3)+len(colonBase3)+len(file_ext)+len(s3)
	
	s5 = ''
	while s4%99 !=0:
		s5+='0'
		s4=s4+1

	fileTail = commaBase3 + file_ext + colonBase3 + s5 + s3
	dnaString = extraModules.base3ToDNABaseWithChar(fileTail,prevChar)
	dnaStringFile.write(dnaString)
	dnaStringFile.flush()
	
	dnaLength  = os.path.getsize(tempPath)
	noOfChunks = dnaLength/99
	noOfBits = int(math.ceil(math.log(noOfChunks,3)))

	dnaStringFile.close()

def generateDNAChunks(readPath,tempPath,savePath):
	xtemp = readPath.split(".")
	dnaFile = file(savePath + "_" + "." + xtemp[len(xtemp) - 1] + FILE_EXT,'wb')
	fileOpened = open(tempPath,"rb")
	fileSize = os.path.getsize(tempPath)

	CHUNK_SIZE = 9900000
	if (fileSize % CHUNK_SIZE) == 0:
		if (fileSize/CHUNK_SIZE) == 0:
			noOfFileChunks = 1
		else:
			noOfFileChunks = (fileSize/CHUNK_SIZE)
	else:
		noOfFileChunks = (fileSize/CHUNK_SIZE) + 1 

	if noOfFileChunks > 1:
		tempString = StringIO()
		tempString.write(fileOpened.read(CHUNK_SIZE))
		dnaString = tempString.getvalue()

		dnaList1 = stringToChunks(dnaString)
		dnaList = ''.join(dnaList1)
		dnaFile.write(dnaList)
		dnaFile.flush()

		del tempString
		del dnaString
		del dnaList

		for chunk_number in range(1,noOfFileChunks):
			tempString = StringIO()
			tempString.write(fileOpened.read(CHUNK_SIZE))
			dnaString = tempString.getvalue()

			dnaList1 = stringToChunks(dnaString)
			dnaList = ''.join(dnaList1)
			dnaFile.write(dnaList)
			dnaFile.flush()

			del tempString
			del dnaString
			del dnaList

	else:
		tempString = StringIO()
		tempString.write(fileOpened.read(CHUNK_SIZE))
		dnaString = tempString.getvalue()

		dnaList1 = stringToChunks(dnaString)
		dnaList = ''.join(dnaList1)
		dnaFile.write(dnaList)
		dnaFile.flush()

		del tempString
		del dnaString
		del dnaList

	gc.collect()
	fileOpened.close()  
	dnaFile.close()

def stringToChunks(string):
	f = []
	global chunkIndex
	global noOfBits
	global noOfChunks
	fileIdentifier = '01'
	if len(string) > 99:
		for j in xrange(0, len(string), 99):
			dnaString = string[j:j+99]
			prevChar = dnaString[-1]
			i3 =  str(extraModules.decimalToBase3(chunkIndex)).zfill(noOfBits)
			parityBit = generateParityBit(i3, fileIdentifier, noOfBits)
			i3 = i3 + fileIdentifier + parityBit
			i3DnaString = extraModules.base3ToDNABaseWithChar(i3,prevChar)
			dnaString += i3DnaString
			f.append(dnaString+"\n")
			chunkIndex +=1
	else:
		f = [string+"\n"]
	return f


def generateParityBit(i3, ID, noOfBits):
	p=int(ID[0])
	for x in range(0,noOfBits):
		p = p + int(i3[x])
		x = x+2
	p = p % 3
	return str(p)
