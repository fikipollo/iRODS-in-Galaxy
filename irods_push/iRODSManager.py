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
'''

import sys
import os
import hashlib
import exceptions
import json
import getpass

from irods.exception import DataObjectDoesNotExist, CollectionDoesNotExist
from irods.models import Collection, User, DataObject
from irods.session import iRODSSession
from password_obfuscation import decode


class IRODSManager:

	#initialize your irods session by reading off irods credentials from .irodsA file and from irods_environment.json file
	def __init__(self):
		"""Initialize the IRODSManager"""
		self.host = ""
		self.port = ""
		self.user = ""
		self.zone = ""
		self.passwd = ""
		self.session = None

	def openSession(self, user_name, passwd=None):
		"""Creates a new session in iRODS"""
		if self.session == None:
			#READ CREDENTIALS FROM CONFIG
			#CREDENTIALS MUST BE STORED IN ~/.irods
			#TODO: ADD CREDENTIALS IN GALAXY CONFIG FILE
			pwFile = "/home/" + getpass.getuser() + "/.irods/.irodsA"
			envFile = "/home/" + getpass.getuser() + "/.irods/irods_environment.json"
			with open(envFile) as f:
				data = json.load(f)

			self.host   =  str(data["irods_host"])
			self.port   =  str(data["irods_port"])
			self.user   =  str(data["irods_user_name"])
			self.zone   =  str(data["irods_zone_name"])

			with open(pwFile) as f:
				first_line = f.readline().strip()
			self.passwd = decode(first_line)

			if(passwd == None):
				#Use default user and password but custom client username and zone
				#TODO CUSTOM CLIENT DIR?
				self.session = iRODSSession(self.host, port=self.port, user=self.user, password=self.passwd, zone=self.zone, client_user=user_name)#, client_zone=client_zone)
			else:
				#Use custom user and password
				#TODO: ZONE?
				self.session = iRODSSession(host=self.host, port=self.port, user=user_name, password=passwd, zone=self.zone)

		return self.session

	def closeSession(self):
		"""Closes the existing session in iRODS"""
		if self.session != None:
			self.session.cleanup()
			del self.session
			self.session = None

	def pushFile(self, origin_file, destination_dir, file_name, overwrite, metadata):
		"""Push a given file to the iRODS server"""
		#Step 1. Check if the origin file is valid
		import os.path
		if not os.path.isfile(origin_file):
			raise IOError("File not found exception: file " + origin_file + " was not found in server." )

		#Step 2. Check if the destination directory exists and is valid for current user
		valid = self.checkDestinationPermissions(destination_dir, metadata["user_name"], file_name)
		if valid == -1:
			raise CollectionDoesNotExist("Destination directory not valid. The path " + destination_dir + " was not found in iRODS." )
		if valid == 1:
			raise CollectionDoesNotExist("Destination directory not valid. The directory " + destination_dir + " in iRODS is not writable for current user." )

		#Step 3. If the file already exists and the overwrite option is false, get the new name
		if overwrite==False and valid == 2:
			aux_fileName = file_name
			i = 0
			while valid == 2:
				print "File " + aux_fileName + " already exits. Generating new name."
				aux_fileName = file_name.split(".")[0]
				try:
					extension = file_name.split(".")[1]
				except Exception as e:
					extension = ""
				i+=1
				aux_fileName = aux_fileName + "_" + str(i) + "." + extension
				print "New name is " + aux_fileName

				valid = self.checkDestinationPermissions(destination_dir, metadata["user_name"], aux_fileName)
			file_name = aux_fileName

		#Step 4. Send the file to iRODS
		self.copyFileToIRODS(destination_dir, origin_file, file_name, metadata)

		#Step 5. Set the metadata for the file
		self.setFileMetadata(destination_dir, file_name, metadata)

		return True

	def pullFile(self, file_path, custom_name, user_name, galaxy_params):
		#Step 1. Check if the origin directory exists and is valid for current user
		file_path = file_path.split("/")
		if len(file_path) < 2:
			raise CollectionDoesNotExist("File path is not valid. The path " + "/".join(file_path) + " was not found in iRODS." )

		fileName = file_path[-1]
		file_path = "/".join(file_path[0:len(file_path)-1]) + "/"

		valid = self.checkDestinationPermissions(file_path, user_name, fileName)
		if valid == -1:
			raise CollectionDoesNotExist("File path not valid. The path " + file_path + " does not exist in iRODS." )
		if valid == 1:
			raise CollectionDoesNotExist("File path not valid. The directory " + file_path + " in iRODS is not readable for current user." )
		if valid == 0:
			raise CollectionDoesNotExist("Unable to find the file '" + file_name + "' in directory " + file_path + " in iRODS.")
		if valid != 2:
			raise CollectionDoesNotExist("Unable to find the file '" + file_name + "' in directory " + file_path + " in iRODS.")

		print "Copying the file from iRODS..."

		#Step 2. Copy the file content to a temporal file
		obj = self.session.data_objects.get(file_path  + fileName)
		with obj.open('r+') as input:
				with open(custom_name,"w") as output:
						output.write(input.read()) #TODO: write to a temporal file?
		output.close()
		input.close()

		print "Registering the file in Galaxy..."

		file_content = {
			"uuid": None,
			"file_type": galaxy_params["file_type"],
			"space_to_tab": False,
			"dbkey": "?",
			"to_posix_lines": True,
			"ext": galaxy_params["file_type"],
			"path": os.path.abspath(output.name),
			"in_place": True,
			"dataset_id": galaxy_params["job_id"],
			"type": "file",
			"is_binary": False, #TODO: GET FROM METADATA
			"link_data_only": "copy_files",
			"name": custom_name
		}

		with open("temporal.json","w") as fileParams:
			fileParams.write(json.dumps(file_content))
		fileParams.close()

		#Step 3. Call to Galaxy's upload tool
		command = "python " + galaxy_params["GALAXY_ROOT_DIR"] + "/tools/data_source/upload.py"\
		+ " " + galaxy_params["GALAXY_ROOT_DIR"]\
		+ " " + galaxy_params["GALAXY_DATATYPES_CONF_FILE"]\
		+ " " + os.path.abspath(fileParams.name)\
		+ " " + galaxy_params["job_id"] + ":" + galaxy_params["output_dir"] + ":" + galaxy_params["output_file"]

		os.system(command)

		return True

	def checkDestinationPermissions(self, destination_dir, user_name, file_name):
		"""This function checks if the destination directory exits and, if so,
		if the current user can write at that directory. Finally the function
		checks if the destination dir already contents a file with the given
		filename

		@returns Integer valid, where
		             -1 destination does not exists
		              1 destination not RW for current user
		              0 valid destination
		              2 valid destination, existing file with same filename
		"""
		# Step 1. Check if destination dir exists
		destination_dir = destination_dir.rstrip("/")

		try:
			self.session.collections.get(destination_dir)
		except Exception as e:
			return -1

		# Step 2. Check if destination dir is R/W for current user
		#TODO: CHECK PERMISSIONS FOR USER
		#return 1

		# Step 3. Check if destination contains a file with same filename
		try:
			self.session.data_objects.get(destination_dir + "/" + file_name)
		except Exception as e:
			pass #does not exists
		else:
			return 2

		return 0

	def copyFileToIRODS(self, destination_dir, origin_file, file_name, metadata):
		"""This function copies a local file to the remote destination directory.
		First the function removes the remote file if already exists. To avoid
		overwriting files, in previous steps the filename should be changed to a
		non-existing remote filename.
		Then the file is copied to the remote server and a validation step is run
		in order to check if the file has been copied succesfully.
		"""
		print "Copying file " + origin_file + " as " + file_name

		# Step 1. Remove the file if exists
		path = os.path.join(destination_dir, file_name)
		try:
			self.session.data_objects.get(path)
			self.session.data_objects.unlink(path)
		except DataObjectDoesNotExist:
			pass

		# Step 2. Create the new file
		print "Saving file as " + path

		obj = self.session.data_objects.create(path)

		# Step 3. Copy the content of the file
		with open(origin_file) as input:
			with obj.open('w') as output:
				for line in input:
					output.write(line)
		input.close()
		output.close()

		# Step 4. Verify content
		local_hash = hashlib.sha256()
		with open(origin_file) as input:
			local_hash.update(input.read())
		remote_hash = hashlib.sha256()
		with obj.open('r') as input:
			remote_hash.update(input.read())

		if local_hash.hexdigest() != remote_hash.hexdigest():
			raise IOError("Verification problem: local file hash does not match remote hash. Maybe the file was not copied correctly." )

		return True

	def setFileMetadata(self, destination_dir, file_name, metadata):
		"""This function sets the metadata for a given file"""
		# Step 1. Check if file exists
		path = os.path.join(destination_dir, file_name)
		obj = self.session.data_objects.get(path)
		if obj == None:
			raise DataObjectDoesNotExist("The object " + path + " was not found at iRODS server." )

		# Step 2. Clear previous metadata
		obj.metadata.remove_all()

		print "Setting metadata to file: " + str(metadata)

		# Step 3. Set metadata
		for key, value in metadata.iteritems():
			obj.metadata.add(key, value)

		return True
