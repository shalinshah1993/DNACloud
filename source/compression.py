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
import threading
import subprocess
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
		
class RepeatingTimer(threading._Timer):
	def run(self):
		while True:
			self.finished.wait(self.interval)
			if self.finished.is_set():
				return
			else:
				self.function(*self.args, **self.kwargs)
				
def progressBarStatus( progressBar ):
	progressBar.UpdatePulse("Compressing the File....This may take several minutes...\n\tso sit back and relax.....")
    
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
	
	progressBar = wx.ProgressDialog('Please wait...', 'Compressing the File....This may take several minutes....\n\t....so sit back and relax....', style = wx.PD_APP_MODAL | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME)
	progressBar.SetSize((450,180))
			
	timer = RepeatingTimer(0.1, progressBarStatus, [ progressBar ])
	timer.daemon = True # Allows program to exit if only the thread is alive
	timer.start()
	
	#subprocess.call blocks till command is executed while subprocess.Popen creates subprocess and returns
	proc = subprocess.Popen( command, stdout = subprocess.PIPE, bufsize=10**8 )
	proc.wait()
	
	progressBar.Destroy()
	timer.cancel()