"""
backup_to_s3.py

One simple strategy for backing up a server to S3: a single backup_to_s3 
function which takes your S3 authentication details plus three (optional)
dictionaries specifying directories, files and commands to be backed up.

e.g:

    backup_to_s3(
        access_key = 'your-access-key',
        secret_access_key = 'your-secret-access-key',
        bucket = 'your-backup-bucket',
        directories = {
            'svnroot': '/var/svnroot',
            'www': '/var/www',
        },
        commands = {
            'test.sql': 'mysqldump -u root test',
        },
        files = {
            'passwd': '/etc/passwd',
        }
    )

The above will create the following temporary directory structure:

/tmp/2008-09-21-17-08-24/
/tmp/2008-09-21-17-08-24/directories/
/tmp/2008-09-21-17-08-24/directories/svnroot/... (copy of /var/svnroot)
/tmp/2008-09-21-17-08-24/directories/www/... (copy of /var/www)
/tmp/2008-09-21-17-08-24/commands/
/tmp/2008-09-21-17-08-24/commands/test.sql (output of mysqldump -u root test)
/tmp/2008-09-21-17-08-24/files/
/tmp/2008-09-21-17-08-24/files/passwd (copy of /etc/passwd)

It will then package that up in to 2008-09-21-17-08-24.tar.gz and save that 
file to 'your-backup-bucket' on S3.

Once it's uploaded the file, it deletes the temporary file and directory.

This script is entirely unsupported. Use and modify at your own risk!
"""

import os, boto, shutil, subprocess, random, datetime
from boto.s3.key import Key

def backup_to_s3(access_key, secret_access_key, bucket, directories = None,
        commands = None, files = None):
    # Most of this command is concerned with copying files in to a single 
    # directory ready to be uploaded to S3
    commands = commands or {}
    files = files or {}
    directories = directories or {}
    
    # Create a directory in /tmp to gather all of the backups
    backup_dir = None
    datestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
    backup_dir = os.path.join('/tmp/', datestamp)
    os.mkdir(backup_dir)
    
    # Backup any directories
    if directories:
        os.mkdir(os.path.join(backup_dir, 'directories'))
        for dirname, src in directories.items():
            dest = os.path.join(backup_dir, 'directories', dirname)
            shutil.copytree(src, dest, symlinks=True)
    
    # Backup any files
    if files:
        os.mkdir(os.path.join(backup_dir, 'files'))
        for filename, src in files.items():
            dest = os.path.join(backup_dir, 'files', filename)
            shutil.copy2(src, dest)
    
    # Run any commands and backup the result
    if commands:
        os.mkdir(os.path.join(backup_dir, 'commands'))
        for filename, command in commands.items():
            dest = os.path.join(backup_dir, 'commands', filename)
            open(dest, 'w').write(get_output(command))
    
    # /tmp/tmp-backup-BLAH is now ready to by tarred and uploaded
    targz = datestamp + '.tar.gz'
    os.chdir('/tmp')
    run_command('tar -zcf %s %s' % (targz, datestamp))
    
    # Now upload that .tar.gz file to S3
    conn = boto.connect_s3(access_key, secret_access_key)
    # This creates the bucket only if it does not already exist:
    try:
        b = conn.get_bucket(bucket)
    except boto.exception.S3ResponseError:
        b = conn.create_bucket(bucket)
    k = Key(b)
    k.key = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S.tar.gz')
    k.set_contents_from_filename(targz)
    
    # Clean-up: delete the local .tar.gz and the local tmp backup directory
    os.remove(targz)
    shutil.rmtree(backup_dir)

# Grr @ Python's dozens of obtuse process handling functions
def get_output(command):
    # Using split() here is a bad idea, will fail on "double quotes"
    return subprocess.Popen(
        command.split(), stdout=subprocess.PIPE
    ).communicate()[0]

run_command = get_output
