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
import json

from iRODSManager import IRODSManager

def main():
	#for now the assumption is that the user is using this tool in a linux environment
	# -- sys.argv[0] is the python script
	# -- sys.argv[1] is the params for the file
	#	  1. File to upload
	#	  2. Custom name
	#	  3. The history ID
	#	  4. Current Galaxy user
	#	  5. Custom user
	#	  6. Custom pass
	# -- sys.argv[2] is the history json

	#Read the params
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
