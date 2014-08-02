"""
#########################################################################
Author: Vijay Dhameliya
Project: DNA Cloud
Graduate Mentor: Dixita Limbachya
Mentor: Prof. Manish K Gupta
Date: 28 July 2013
Website: www.guptalab.org/dnacloud
This file contains implementation of various compression techniques.
#########################################################################
"""

import bz2
import wx
import os
import sys
import time
import Image
import Queue
import threading
import subprocess
import extraModules
from cStringIO import StringIO

FFMPEG_BIN = ""
if hasattr(sys, "frozen"):
        PATH = os.path.dirname(sys.executable)
else:
        PATH = os.path.dirname(os.path.abspath(__file__))
        
if "linux" in sys.platform or 'darwin' in sys.platform:
		FFMPEG_BIN = PATH + "/../scripts/ffmpeg"
elif "win" in sys.platform and not 'darwin' in sys.platform:
		FFMPEG_BIN = PATH + "\..\scripts\ffmpeg.exe"

# returns path of compressed file, this function is called before compressing any file
# so write path can be passed to compress funtion
def compressedFilePath (readPath, WORKSPACE_PATH, compType):
	
	inputFilename = os.path.basename( readPath )
	inputFilenameNoExtension = os.path.splitext( inputFilename )[0]
	inputFileExtension = os.path.splitext( inputFilename )[1]
		
	compressFilePath = ''
	if "win" in sys.platform and not 'darwin' in sys.platform:
		compressFilePath = WORKSPACE_PATH + '\.temp\comp_'
	elif "linux" in sys.platform or 'darwin' in sys.platform:
		compressFilePath = WORKSPACE_PATH + '/.temp/comp_'
	
	if compType == 1:
		compressFilePath += inputFilename + '.bz2'
	elif compType == 2:
		if not extraModules.getFileType( readPath ):
			compressFilePath = None
		elif "image" in extraModules.getFileType( readPath ):
			compressFilePath += inputFilenameNoExtension + ".jpeg"
		elif "video" in extraModules.getFileType( readPath ):
			compressFilePath += inputFilename
		elif "music" in extraModules.getFileType( readPath ):
			compressFilePath += inputFilename
		else:
			compressFilePath = None
	else:
		compressFilePath = None
			
	return compressFilePath
	
# reads file from readPath and compress it according to compType and stores it at savePath
def compress( readPath, savePath, compType ):
	
	if compType == 1:
		if not os.path.isfile( savePath ):
			compressFileToBz2( readPath, savePath )
	elif compType == 2:
		if not extraModules.getFileType( readPath ):
			print "Lossy compression not possible for selected file type"
		elif "image" in extraModules.getFileType( readPath ):
			if not os.path.isfile( savePath ):\
				compressImageFile( readPath, savePath )
		elif "video" in extraModules.getFileType( readPath ):
			if not os.path.isfile( savePath ):
				compressMediaFile( readPath, savePath, "video" )
		elif "music" in extraModules.getFileType( readPath ):
			if not os.path.isfile( savePath ):
				compressMediaFile( readPath, savePath, "audio" )
    
def compressFileToBz2( filePath, storePath ):
	fileOpened = open( filePath, "rb" )
	compressedFile = file( storePath, 'wb' )
	fileOpened.seek(0,0)
	compressedString = bz2.compress( fileOpened.read() )
	compressedFile.write( compressedString )
	fileOpened.close()
	compressedFile.close()

def decompressFileFromBz2( filePath, storePath ):
	fileOpened = open( filePath, "rb" )
	decompressedFile = file( storePath, 'wb' )
	fileOpened.seek(0,0)
	decompressedString = bz2.decompress( fileOpened.read() )
	decompressedFile.write( decompressedString )
	fileOpened.close()
	decompressedFile.close()

def compressImageFile( filePath, storePath, compressRatio = -1 ):
	img = Image.open( filePath )
	compressedImg = file( storePath, 'wb' )
	tmp = StringIO()
	img.save(tmp, 'JPEG', quality = 80)
	tmp.seek(0)
	compressedImg.write( tmp.getvalue() )
	tmp.close()
	compressedImg.close()
	
def compressMediaFile( filePath, storePath , mediaType, compressRatio = -1 ):
	
	if not FFMPEG_BIN:
		print "FFmpeg not found"
		return
		
	if compressRatio == -1:
		command = [ FFMPEG_BIN, '-i', filePath, storePath]
	elif "video" in mediaType:
		command = [ FFMPEG_BIN, '-i', filePath, '-b:v', str(compressRatio) + 'k' , storePath]
	
	proc = subprocess.call( command, stdout = subprocess.PIPE, bufsize=10**8 )
