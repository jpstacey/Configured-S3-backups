#!/usr/bin/env python
#
# Get a config file from disk

import ConfigParser
import os

_root = '.backup_to_s3'

def getconf(key, root=_root, subconf = None):
    conf_dir = os.environ.get("HOME")
    p = ConfigParser.ConfigParser()
    p.read( ("%s/%s/%s.conf" % (conf_dir, root, key),) )

    conf = {}
    for sec in p.sections():
        conf[sec] = {}
        for (k,v) in p.items(sec):
            conf[sec][k] = v

    if subconf is None:
      return conf
    return conf[subconf]

def findconfs(root=_root, excluding=[]):
    conf_dir = os.environ.get("HOME")
    confs = [d[:-5] for d in os.listdir("%s/%s" % (conf_dir, root)) if d.endswith(".conf")]
    return [c for c in confs if c not in excluding]
