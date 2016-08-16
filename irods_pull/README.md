# iRODS pull for GALAXY

Use this tool to load a file from your iRODS filesystem into the current Galaxy history.

**Note**: this tool requires the _python-irodsclient_ API installed in the Galaxy instance. See root tool repository for installation instructions.

**Note**: by default the iRODS session will be created using the credentials stored at the *.irodsA* and the *irods_environment.json* files unless the user provides some custom credentials. Instructions for creating these files are available at the root tool repository.

At the end of this document you can find some screenshots for this tool.

### How to install
1. Copy the whole directory at the Galaxy tools directory
```bash
cp -r tmp_dir/irods_pull /usr/local/galaxy/tools/irods_pull
```
2. Optionally you can install the JavaScript file browser for iRODS and the iRODS tools for Galaxy API. For futher information read the documentation at the root of this repository.

3. Register the new tool in Galaxy. Add a new entry at the tool_conf.xml file in the desired section.  
```bash
vi /usr/local/galaxy/config/tool_conf.xml
```  
```xml
<?xml version='1.0' encoding='utf-8'?>
<toolbox monitor="true">
    <section id="getext" name="Get Data">
       <tool file="data_source/upload.xml" />
       <tool file="irods_pull/irods_pull.xml" />
       [...]
```

4. Restart Galaxy

### How to use

First choose the file in iRODS using the directory browser (if available).
Alternatively, you can write the complete path to the file in iRODS.

Then, set a custom name for the file in Galaxy (optional) and click on "Execute".

By default, the tool will use your galaxy username as iRODS user.
If you want to use your own iRODS credentials choose the option *Use custom credentials* and fill the corresponding fields.

### Some screenshots
*The tool in Galaxy*

![alt text][screenshot1]

--------
*Using the directory browser to choose the file in iRODS*

![alt text][screenshot2]

[screenshot1]: ../other/irods_pull_image1.png "The tool in Galaxy"

[screenshot2]: ../other/irods_pull_image2.png "Using the directory browser to choose the file in iRODS"
