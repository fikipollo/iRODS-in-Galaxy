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

	  A Galaxy tool to retrieve files from an external iRODS server.
'''

import sys
import json

from iRODSManager import IRODSManager

def main():
	"""
	This function reads the params and retrieves a file from an iRODS server using
	the 'pullFile' function	defined in the IRODSManager class. Credentials for
	iRODS should be stored in the Galaxy server.

	Note: this tool requires the python-irodsclient API installed in the Galaxy instance.

	The accepted params are:
	 -- sys.argv[0] is the python script
	 -- sys.argv[1] is a JSON-like string containing the params for the script
		  1. file_path, the path for the file to retrieve in iRODS
		  2. custom_name, custom name for the file in Galaxy
		  3. user_name, current Galaxy username
		  4. custom_user, custom user for iRODS (optional)
		  5. custom_pass, custom pass for iRODS (optional)
		  6. job_id, the identifier for current galaxy job
		  7. output_dir, path for the output directory for current job
		  8. output_file, name for the output file for current job
		  9. file_type, type of the loaded file
		 10. GALAXY_ROOT_DIR
		 11. GALAXY_DATATYPES_CONF_FILE
	"""
    #STEP 1. Read the params
	params = json.loads(sys.argv[1])

	custom_user = params["user_name"]
	custom_pass = None
	if "custom_user" in params:
		custom_user = params["custom_user"]
		custom_pass = params["custom_pass"]

	#STEP 3. LOAD THE FILE USING iRODS API
	irodsManager = IRODSManager()
	irodsManager.openSession(custom_user, custom_pass)
	irodsManager.pullFile(params["file_path"], params["custom_name"], params["user_name"], params)
	irodsManager.closeSession()

	return ""

if __name__ == "__main__":
	main()
