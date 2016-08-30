#!/usr/bin/python
'''
   The MIT License (MIT)

   Copyright (c) 2016 SLU Global Bioinformatics Centre, SLU

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.

   Contributors:
      Rafael Hernandez de Diego <rafahdediego@gmail.com>
      Tomas Klingstrom
      Erik Bongcam-Rudloff
      and others.

   API operations for iRODS
'''

from __future__ import absolute_import

import logging
import urllib

from galaxy import exceptions, util
from galaxy.model.item_attrs import UsesAnnotations
from galaxy.web import _future_expose_api as expose_api
from galaxy.web.base.controller import BaseAPIController, url_for, UsesStoredWorkflowMixin
from galaxy.web.base.controller import SharableMixin

from irods.session import iRODSSession
from irods.exception import DataObjectDoesNotExist

import getpass
import json

log = logging.getLogger(__name__)

class IRODSAPIController(BaseAPIController, UsesStoredWorkflowMixin, UsesAnnotations, SharableMixin):

	def __init__( self, app ):
		super( IRODSAPIController, self ).__init__( app )
		self.host = ""
		self.port = ""
		self.user = ""
		self.zone = ""
		self.passwd = ""
		self.session = None

	@expose_api
	def index(self, trans, payload, **kwd):
		"""
		POST /api/external/irods

		Displays a collection of files stored in an external iRODS server,
		for the current Galaxy user, or using the provided credentials.

		Note: this tool requires the python-irodsclient API installed in the Galaxy instance.

		Note: by default the iRODS session will be created using the credentials stored
 		      at the .irodsA and the irods_environment.json files unless the user provides
			  some custom credentials.
			  Instructions for creating these files are available at the tool repository.

		@param	trans
		@param	payload
		@return the directories tree in JSON format.

		"""
		#STEP 1. READ THE PARAMS
		client_user = payload.get("username", trans.user.username )
		client_passwd = payload.get("password", None)
		#IF THE REQUEST DOES NOT INCLUDE THE FLAG "show_files", SHOW ONLY DIRECTORIES
		show_files = False
		if "show_files" in payload:
			show_files = payload[ 'show_files' ]

		# ALTERNATIVE 1 ------------------------------------------------------------
		#   CHECK ALL THE DIRECTORIES IN THE TREE AND GET ALL THE DIRS THAT
		#   ARE WRITABLE BY THE USER
		#   THIS OPTION COULD BE SLOW IF iRODS IS FULL OF DATA, IN THAT CASE, THE
		#   ALTERNATIVE 2 REDUCES TIMES BUT IS LESS EFECTIVE
		#----------------------------------------------------------------------------
		root = "/" + self.zone + "/home/"
		results = ""
		try:
			#STEP 2. OPEN A NEW SESSION AS ROOT
			self.openSession();
			coll = self.session.collections.get("/b3devZone")
			#Get all the directories and files
			tree = coll.walk()
			self.closeSession();

			#STEP 3. OPEN A NEW SESSION AS CLIENT
			self.openSession(client_user, client_passwd);

			#STEP 4. REMOVE ALL NOT VALID PATHS FOR THE USER
			valid = []
			for node in tree:
				if self.session.collections.exists(node[0].path):
					valid.append((node[0].path, node[2]))

			#STEP 5. GENERATE THE TREE
			ALL_NODES = {}
			for node in valid:
				#get existing or create a new new
				newNode = ALL_NODES.get(node[0], {"name" : node[0].split("/")[-1], "children": [], "type": "dir"})
				if show_files:
					for f in node[1]:
						newNode["children"].append({"name" : f.path.replace(node[0] + "/", ""), "type": "file"})
				#Using this flag we discriminate which directories are valid for selection
				newNode["allow"] = 1
				#Add the node to the tree
				parentNode = self.getParentNode("/".join(node[0].split("/")[0:-1]), ALL_NODES)
				parentNode["children"].append(newNode)
				ALL_NODES[node[0]] = newNode

			results = ALL_NODES["/"]

		# ALTERNATIVE 2 ------------------------------------------------------------
		#   CHECKS ONLY THE HOME DIRECTORY FOR THE CURRENT USER AND GETS ALL THE
		#   DIRS THAT ARE WRITABLE BY THE USER
		#   THIS OPTION IS FASTER BUT IS LESS EFECTIVE AND IGNORE OTHER DIRECTORIES
		#----------------------------------------------------------------------------
		#	#STEP 2. OPEN A NEW SESSION
		#	self.openSession(client_user, client_passwd);
		#
		#	#STEP 3. GET THE DIRECTORY CONTENTS
		#	#WE ONLY SHOW THE HOME DIR
		#	root = "/" + self.zone + "/home/"
		#	collection = self.session.collections.get(root + client_user)
		#	results = self.getCollectionAsTree(collection, show_files, root)
		except Exception as e:
			results = str(e)
			pass
		finally:
			#CLOSE SESSION
			self.closeSession();
		return [results]

	def openSession(self, user_name=None, passwd=None):
		"""
		This function creates a new session in iRODS

		Note: by default the iRODS session will be created using the credentials stored
 		      at the .irodsA and the irods_environment.json files unless the user provides
			  some custom credentials.
			  Instructions for creating these files are available at the tool repository.
		"""
		if self.session == None:
			#READ CREDENTIALS FROM THE CONFIG FILES STORED IN ~/.irods AFTER USING iCommands
			#CREDENTIALS MUST BE STORED IN ~/.irods
			#TODO: ADD THE iRODS CREDENTIALS IN THE GALAXY CONFIG FILE
			pwFile = "/home/" + getpass.getuser() + "/.irods/.irodsA"
			envFile = "/home/" + getpass.getuser() + "/.irods/irods_environment.json"

			with open(envFile) as f:
				data = json.load(f)

			self.host   =  str(data["irods_host"])
			self.port   =  str(data["irods_port"])
			self.user   =  str(data["irods_user_name"])
			self.zone   =  str(data["irods_zone_name"])

			if(user_name == None): #Root connection
				#Use default user and password but custom client username and zone
				with open(pwFile) as f:
					first_line = f.readline().strip()
				self.passwd = decode(first_line)
				#TODO: use custom directory client_zone (form)
				self.session = iRODSSession(self.host, port=self.port, user=self.user, password=self.passwd, zone=self.zone)#, client_zone=client_zone)
			elif(passwd == None):
				#Use default user and password but custom client username and zone
				with open(pwFile) as f:
					first_line = f.readline().strip()
				self.passwd = decode(first_line)
				#TODO: use custom directory client_zone (form)
				self.session = iRODSSession(self.host, port=self.port, user=self.user, password=self.passwd, zone=self.zone, client_user=user_name)#, client_zone=client_zone)
			else:
				#Use custom user and password
				#TODO: use custom directory client_zone (form)
				self.session = iRODSSession(host=self.host, port=self.port, user=user_name, password=passwd, zone=self.zone)

		return self.session

	def closeSession(self):
		"""
		This function closes the existing session in iRODS
		"""
		if self.session != None:
			self.session.cleanup()
			del self.session
			self.session = None
		return True

	def getCollectionAsTree(self, collection, show_files, root=None):
		"""
		This function gets the sub-directories tree for a given root.

		@param	collection the collection to browse
		@param	show_files if true, includes all the files in a directory
		@param	root, the first directory to explore
		@return the directories tree in JSON format.
		"""
		tree={"name" : collection.name, "children": [], "type": "dir", "allow" : 1}
		for col in collection.subcollections:
			tree["children"].append(self.getCollectionAsTree(col, show_files))
		if show_files:
			for obj in collection.data_objects:
				tree["children"].append({"name" : obj.name, "type": "file"})

		if root != None:
			root = root.rstrip("/").split("/")
			root.reverse()
			for _dir in root:
				_dir = (_dir or "/")
				tree={"name" : _dir, "children": [tree], "type": "dir", "allow" : 0}

		return tree

	def getParentNode(self, parentNodePath, ALL_NODES):
		if parentNodePath in ALL_NODES:
			return ALL_NODES.get(parentNodePath)
		if parentNodePath == "":
			newNode={"name" : "/", "children": [], "type": "dir", "allow" : 0}
			ALL_NODES["/"] = newNode
			return newNode
		else:
			newNode = {"name" : parentNodePath.split("/")[-1], "children": [], "type": "dir", "allow" : 0}
			parentNode = self.getParentNode("/".join(parentNodePath.split("/")[0:-1]), ALL_NODES)
			parentNode["children"].append(newNode)
			ALL_NODES[parentNodePath] = newNode
			return newNode



"""
This file is part of the iRODS project.
Copyright (c) 2005-2016, Regents of the University of California, the University
of North Carolina at Chapel Hill, and the Data Intensive Cyberinfrastructure
Foundation

https://github.com/irods/irods/blob/master/scripts/irods/password_obfuscation.py
"""
import os

seq_list = [
        0xd768b678,
        0xedfdaf56,
        0x2420231b,
        0x987098d8,
        0xc1bdfeee,
        0xf572341f,
        0x478def3a,
        0xa830d343,
        0x774dfa2a,
        0x6720731e,
        0x346fa320,
        0x6ffdf43a,
        0x7723a320,
        0xdf67d02e,
        0x86ad240a,
        0xe76d342e
    ]

#Don't forget to drink your Ovaltine
wheel = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/'
    ]

default_password_key = 'a9_3fker'
default_scramble_prefix = '.E_'

#Decode a password from a .irodsA file
def decode(s, uid=None):
    #This value lets us know which seq value to use
    #Referred to as "rval" in the C code
    seq_index = ord(s[6]) - ord('e')
    seq = seq_list[seq_index]

    #How much we bitshift seq by when we use it
    #Referred to as "addin_i" in the C code
    #Since we're skipping five bytes that are normally read,
    #we start at 15
    bitshift = 15

    #The uid is used as a salt.
    if uid is None:
        uid = os.getuid()

    #The first byte is a dot, the next five are literally irrelevant
    #garbage, and we already used the seventh one. The string to decode
    #starts at byte eight.
    encoded_string = s[7:]

    decoded_string = ''

    for c in encoded_string:
        if ord(c) == 0:
            break
        #How far this character is from the target character in wheel
        #Referred to as "add_in" in the C code
        offset = ((seq >> bitshift) & 0x1f) + (uid & 0xf5f)

        bitshift += 3
        if bitshift > 28:
            bitshift = 0

        #The character is only encoded if it's one of the ones in wheel
        if c in wheel:
            #index of the target character in wheel
            wheel_index = (len(wheel) + wheel.index(c) - offset) % len(wheel)
            decoded_string += wheel[wheel_index]
        else:
            decoded_string += c

    return decoded_string
