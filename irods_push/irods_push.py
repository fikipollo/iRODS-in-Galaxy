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
        Tomas Klingström
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
    #      1. Destination directory
    #      2. Overwrite option
    #      3. The history ID
    #      4. The selected dataset id
    #      5. The selected dataset name
    #      6. The selected dataset file name
    #      7. The selected dataset file format
    #      8. Current Galaxy user
    #      9. Custom user
    #      10. Custom pass
    # -- sys.argv[2] is the history json

    #Read the params
    params = eval(sys.argv[1])
    history_json = json.loads(sys.argv[2])

    destination_dir = params[0]
    overwrite = (params[1] == "true")

    file_name = params[4]
    origin_file = params[5]

    metadata = {
        "history_id" : params[2],
        "dataset_id" : params[3],
        "format"     : params[6],
        "user_name"  : params[7]
    }

    custom_user = None
    custom_pass = None

    if len(params) > 8:
        custom_user = params[8]
        custom_pass = params[9]

    #STEP 2. COMPLETE THE METADATA FOR THE FILE USING THE GALAXY API
    #GENERATE THE provenance
    datasets_table = {}
    provenance_list = []
    already_added = {}
    origin_job = None
    # 1. Process the history data and generate the table dataset -> job id
    for job_id, job_instance in history_json.iteritems():
        for output_item in job_instance["outputs"]:
            datasets_table[output_item["id"]] = job_instance
            if output_item["id"] == metadata["dataset_id"]:
                origin_job=job_instance

    # 2. Get the origin job
    provenance_list = generateProvenance(origin_job, datasets_table, provenance_list, already_added)
    metadata["provenance"] = json.dumps(provenance_list);
    # print metadata["provenance"]

    #STEP 3. SEND THE FILE TO iRODS API
    irodsManager = IRODSManager()

    if custom_user != None:
        irodsManager.openSession(custom_user, custom_pass)
    else:
        irodsManager.openSession(metadata["user_name"], None)

    irodsManager.pushFile(origin_file, destination_dir, file_name, overwrite, metadata)
    irodsManager.closeSession()

    return ""

def generateProvenance(job_instance, datasets_table, provenance_list, already_added):
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
