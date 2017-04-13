import synapseclient
from synapseclient.entity import is_container
import os
import json

def getChildren(syn, parentId):
    pass
    #return((_getChildren))

def _getChildren(syn, parentId, includeTypes=["folder","file","table","link","entityview","dockerrepo"], sortBy="NAME", sortDirection="ASC", nextPageToken=None):
    #parentId = "syn5522959"
    entityChildrenRequest = {'parentId':parentId,
                             'includeTypes':includeTypes,
                             'sortBy':sortBy,
                             'sortDirection':sortDirection,
                             'nextPageToken':nextPageToken}

    page = syn.restPOST('/entity/children',body =json.dumps(entityChildrenRequest))
    yield page['page']
    if page.get('nextPageToken') is not None:
        for x in _getChildren(syn, parentId, includeTypes=["folder","file","table","link","entityview","dockerrepo"], sortBy="NAME", sortDirection="ASC", nextPageToken=page.get('nextPageToken')):
            yield x


def walk(syn, synId):
    """
    Traverse through the hierarchy of files and folders stored under the synId. Has the same behavior
    as os.walk()

    :param syn:            A synapse object: syn = synapseclient.login()- Must be logged into synapse

    :param synId:          A synapse ID of a folder or project

    Example::

        walkedPath = walk(syn, "syn1234")

        for dirpath, dirname, filename in walkedPath:
            print(dirpath)
            print(dirname) #All the folders in the directory path
            print(filename) #All the files in the directory path

    """
    return(_helpWalk(syn,synId))

#Helper function to hide the newpath parameter
def _helpWalk(syn,synId,newpath=None):
    starting = syn.get(synId,downloadFile=False)
    #If the first file is not a container, return immediately
    if newpath is None and not is_container(starting):
        return
    elif newpath is None:
        dirpath = (starting.name, synId)
    else:
        dirpath = (newpath,synId)
    dirs = []
    nondirs = []
    results = syn.chunkedQuery('select id, name, nodeType from entity where parentId == "%s"'%synId)
    for i in results:
        if is_container(i):
            dirs.append((i['entity.name'],i['entity.id']))
        else:
            nondirs.append((i['entity.name'],i['entity.id']))
    yield dirpath, dirs, nondirs
    for name in dirs:
        newpath = os.path.join(dirpath[0],name[0])
        for x in _helpWalk(syn, name[1], newpath):
            yield x


