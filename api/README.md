# iRODS tools for GALAXY API

This tool extends the API Galaxy adding support for manipulating files on an external iRODS server.

**Note**: this tool requires the _python-irodsclient_ API installed in the Galaxy instance. See root tool repository for installation instructions.

**Note**: by default the iRODS session will be created using the credentials stored at the *.irodsA* and the *irods_environment.json* files unless the user provides some custom credentials. Instructions for creating these files are available at the root tool repository.

At the end of this document you can find installation instructions for this tool.

### Supported actions

The actions supported for the current version are:

#### List the contents of a directory [**POST**].  
Returns the contents of a directory, including or excluding files, and its subdirectories.  

**Params:**
- **key** (_optional_):  the API key for the user, required if no galaxy session is opened.
- **show_files** (_optional_): if true, the response will include also the files for each directory.
- **username** (_optional_): custom user for iRODS
- **password** (_optional_): custom password for iRODS

**Example of use:**

Example POST request sent using jQuery:
```javascript
$.ajax({
	method: "POST",
	url: "localhost:8080/galaxy/api/external/irods/",
	data: {
		show_files: true
	},
	success: function( data ) {
		console.log( data );
	}
});
```

Returns a JSON object describing the tree for the home directory for current galaxy user.

```javascript

[
  {
    "type": "dir",
    "name": "/",
    "children": [
      {
        "type": "dir",
        "name": "irodstestzone",
        "children": [
          {
            "type": "dir",
            "name": "home",
            "children": [
              {
                "type": "dir",
                "name": "rafael",
                "children": [
                  {
                    "type": "file",
                  	"name": "rnaseq_mm10.tab"
                  },
                  {
                  	"type": "file",
                  	"name": "mm10_reference.gtf"
                  },
                  ...
                ]
              }
            ]
          }
        ]
      }
    ]
  }
]
```

### How to install

- Copy the **irods.py** file at the Galaxy API directory.

```bash
cp tmp_dir/irods.py /usr/local/galaxy/lib/galaxy/webapps/galaxy/api/irods.py
```
- Register the new API entry in Galaxy.  
Edit the following file adding the lines below at the end of the function **populate_api_routes**:  

```bash
vi /usr/local/galaxy/lib/galaxy/webapps/galaxy/buildapp.py
```

```python

def populate_api_routes( webapp, app ):
	[...]
	# controller="metrics", action="show", conditions=dict( method=["GET"] ) )
	webapp.mapper.connect( "create", "/api/metrics"...)

	# ============================
	# ===== iRODS        API =====
	# ============================
	webapp.mapper.connect('irods_file_retrieval',
                           '/api/external/irods/',
                           controller='irods',
                           action='index',
                           conditions=dict( method=[ "POST" ] ) )


def _add_item_tags_controller( webapp, name_prefix, path_prefix, **kwd ):
	[...]
```

- Restart Galaxy
