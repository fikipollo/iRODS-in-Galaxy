# iRODS push for GALAXY

Use this tool to save files from the current Galaxy history to the selected location in your iRODS filesystem.
This tool also stored some metadata for each file, including the author (galaxy user), history identifier, and
the *file provenance*.

**Note**: this tool requires the _python-irodsclient_ API installed in the Galaxy instance. See root tool repository for installation instructions.

**Note**: by default the iRODS session will be created using the credentials stored at the *.irodsA* and the *irods_environment.json* files unless the user provides some custom credentials. Instructions for creating these files are available at the root tool repository.

At the end of this document you can find some screenshots for this tool.

### How to install
1. Copy the whole directory at the Galaxy tools directory
```bash
cp -r tmp_dir/irods_push /usr/local/galaxy/tools/irods_push
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
       [...]
    <section id="send" name="Send Data">
       <tool file="genomespace/genomespace_exporter.xml" />
       <tool file="irods_push/irods_push.xml" />
       [...]
```

4. Restart Galaxy

### How to use

First choose the directory in iRODS where the files will be saved using the directory browser (if available).
Alternatively, you can write the complete path to the destination directory.

Then, choose the file(s) that you want to save and click on "Execute".

By default, the tool will use your galaxy username as iRODS user.
If you want to use your own iRODS credentials choose the option *Use custom credentials* and fill the corresponding fields.

**Note**: By default files are not overwrited so if a file already exists at the specified folder (with the same name), by default the new file will be stored with an automatic suffix (e.g. myfile_2.txt).
You can change the default behaviour by checking the corresponding option at the form. Use this option with caution and always at your own risk.


### Some screenshots
*The tool in Galaxy*

![alt text][screenshot1]

--------
*Using the directory browser to choose the file in iRODS*

![alt text][screenshot2]

[screenshot1]: ../other/irods_push_image1.png "The tool in Galaxy"

[screenshot2]: ../other/irods_push_image2.png "Using the directory browser to choose the destination directory in iRODS"
