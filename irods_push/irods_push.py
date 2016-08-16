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

	  A Galaxy tool to store files in an external iRODS server.
'''

import sys
import json

from iRODSManager import IRODSManager

def main():
	"""
	This function reads the params and sends a file from the Galaxy history to an
	iRODS server using the 'pushFile' function defined in the IRODSManager class.
	Credentials for iRODS should be stored in the Galaxy server.

	Note: this tool requires the python-irodsclient API installed in the Galaxy instance.

	The accepted params are:
	 -- sys.argv[0] is the python script
	 -- sys.argv[1] is a JSON-like string containing the params for the script
		  1. destination_dir, the path for the destination directory in iRODS
		  2. overwrite, overwrite or keep existing files with same name
		  3. history_id, the current history identifier
		  4. dataset_id, the identifier for the selected dataset
		  5. dataset_name, the name for the selected dataset
		  6. file_name, the file name for the selected dataset
		  7. file_format, the file format for the selected dataset
		  8. user_name, current Galaxy username
		  9. custom_user, custom user for iRODS (optional)
		 10. custom_pass, custom pass for iRODS (optional)
	 -- sys.argv[2] is the current Galaxy history in JSON-like format
	"""
	#STEP 1. Read the params
	params = json.loads(sys.argv[1])
	history_json = json.loads(sys.argv[2])

	custom_user = params["user_name"]
	custom_pass = None
	if "custom_user" in params:
		custom_user = params["custom_user"]
		custom_pass = params["custom_pass"]

	#STEP 2. COMPLETE THE METADATA FOR THE FILE USING THE GALAXY API
	# 2.a. FROM INPUT PARAMS
	metadata = {
		"history_id" : params["history_id"],
		"dataset_id" : params["dataset_id"],
		"format"     : params["file_format"],
		"user_name"  : params["user_name"]
	}

	# 2.b. GENERATE THE PROVENANCE FOR THE FILE BASED ON THE HISTORY
	datasets_table = {}
	provenance_list = []
	already_added = {}
	origin_job = None
	#   2.b.i. Process the history data and generate the table dataset -> job id
	for job_id, job_instance in history_json.iteritems():
		for output_item in job_instance["outputs"]:
			datasets_table[output_item["id"]] = job_instance
			if output_item["id"] == metadata["dataset_id"]:
				origin_job=job_instance

	#   2.b.ii. Get the origin job
	provenance_list = generateProvenance(origin_job, datasets_table, provenance_list, already_added)
	metadata["provenance"] = json.dumps(provenance_list);

	#STEP 3. UPLOAD THE FILE USING THE iRODS API
	irodsManager = IRODSManager()
	irodsManager.openSession(custom_user, custom_pass)
	irodsManager.pushFile(params["file_name"], params["destination_dir"], params["dataset_name"], (params["overwrite"] == "true"), metadata)
	irodsManager.closeSession()

	return ""

def generateProvenance(job_instance, datasets_table, provenance_list, already_added):
	"""
	This function generates the provenance for a given dataset from a the Galaxy history.
	Starting from the job that results in the dataset, the script goes back in the history
	selecting all the jobs whose results were used to produce the final dataset.
	"""
	#if not in provenance_list --> push
	if not job_instance["id"] in already_added:
		already_added[job_instance["id"]] = 1
		provenance_list.append(job_instance)

	#Get the input files
	#For each input file, get the origin job
	for input_item in job_instance["inputs"]:
		origin_job = datasets_table[input_item["id"]]
		generateProvenance(origin_job, datasets_table, provenance_list, already_added)

	return provenance_list

if __name__ == "__main__":
	main()
