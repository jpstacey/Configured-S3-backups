#!/usr/bin/env python
"""
Backup using backup_to_s3.py and python-boto
"""

import sys

from backup_to_s3 import backup_to_s3
from getconf import getconf, findconfs

def _backup_to_s3(access_key, secret_access_key, bucket, directories = {}, commands = {}, files = {}):
    print " > " + bucket

    print " > directories"
    for d,dd in directories.items(): print "  > %s : %s" % (d,dd)
    print " > commands"
    for d,dd in commands.items(): print "  > %s : %s" % (d,dd)
    print " > files"
    for d,dd in files.items(): print "  > %s : %s" % (d,dd)

keys = getconf('INIT', subconf='keys')
confs = findconfs(excluding=('INIT',))

# Optional command-line filter
try: confs = [c for c in confs if c == sys.argv[1] or sys.argv[1] == 'ALL']
except IndexError: pass

for conf_name in confs:
    conf = getconf(conf_name)
    label = conf['META'].get('label', "Unnamed backup %s" % conf_name)
    print "Starting backup: '%s'" % label

    args = {
      'access_key': keys['access'],
      'secret_access_key': keys['secret'],

      'bucket': conf['META']['bucket'],

      'directories': conf.get('directories', {}),
      'commands': conf.get('commands', {}),
      'files': conf.get('files', {}),
    }
    _backup_to_s3(**args)
    if len(sys.argv) == 3 and sys.argv[2] == "go":
        backup_to_s3(**args)
    else:
        print "DRY RUN"

    print "Finishing backup: '%s'\n" % label

if not confs:
    print "No conf files: nothing to do."
