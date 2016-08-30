#SOME TEST CODE FOR LEARNING HOW TO USE THE IRODS API FOR PYTHON...

from irods.session import iRODSSession
from irods.exception import DataObjectDoesNotExist

sess = iRODSSession(host='192.168.99.100', port=32771, user='foo', password='foo', zone='fooZone')
coll = sess.collections.get("/fooZone/home/foo")

for col in coll.subcollections:
	print col

for obj in coll.data_objects:
	print c

#for obj in coll.data_objects:
#	obj.unlink()

coll = sess.collections.get("/fooZone/home/rafa")

for col in coll.subcollections:
	print col

for obj in coll.data_objects:
	print c

#for obj in coll.data_objects:
#	obj.unlink()

tree = coll.walk()
for node in tree:
	print node



def getParentNode(parentNodePath, ALL_NODES):
	if parentNodePath in ALL_NODES:
		return ALL_NODES.get(parentNodePath)
	if parentNodePath == "":
		newNode={"name" : "/", "children": [], "type": "dir"}
		ALL_NODES["/"] = newNode
		return newNode
	else:
		newNode = {"name" : parentNodePath.split("/")[-1], "children": [], "type": "dir"}
		parentNode = getParentNode("/".join(node[0].split("/")[0:-1]), ALL_NODES)
		parentNode["children"].append(newNode)
		ALL_NODES[parentNodePath] = newNode
		return newNode

sess1 = iRODSSession(host='192.168.99.100', port=32771, user='foo', password='foo', zone='fooZone')
sess2 = iRODSSession(host='192.168.99.100', port=32771, user='foo', password='foo', zone='fooZone', client_user="rafa")

coll = sess1.collections.get("/fooZone")
tree = coll.walk()
valid = []
for node in tree:
	if sess2.collections.exists(node[0].path):
		valid.append((node[0].path, node[2]))

ALL_NODES = {}
for node in valid:
	parentNode = getParentNode("/".join(node[0].split("/")[0:-1]), ALL_NODES)
	newNode = {"name" : node[0].split("/")[-1], "children": [], "type": "dir"}
	for f in node[1]:
		newNode["children"].append({"name" : f.path.replace(node[0] + "/", ""), "type": "file"})
	parentNode["children"].append(newNode)
	ALL_NODES[node[0]] = newNode


currentDir = tree
for node in valid:
	path = node[0].split("/")
	for directory in path:
		if directory = "":
			directory = "/"
		if directory == currentDir["name"]:
			for f in node[1]:
