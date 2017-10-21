#!/usr/bin/python
import argparse
import os.path
import os
import subprocess
import time
from time import gmtime, strftime
from subprocess import call

## Process arguments
parser = argparse.ArgumentParser(description='Elasticsearch Backup/Restore script.')
parser.add_argument('--backup', action='store_true', dest='backup', help='...')
parser.add_argument('--restore', action='store_true', dest='restore', help='...')
parser.add_argument('--migrate', action='store_true', dest='migrate', help='...')
parser.add_argument('-u', action='store', dest='source', help='Source Elasticsearch URL')
parser.add_argument('-d', action='store', dest='path', help='Backup Data Directory')
parser.add_argument('-i', action='store', dest='import', help='Import Data Directory')
parser.add_argument('-t', action='store', dest='target', help='Target Elasticsearch URL')
args = parser.parse_args()

if not args.backup and not args.restore and not args.migrate:
    parser.parse_args(['-h'])

def backup(source, path):
    print "Start backup"
    
    ## Check URL
    sourceURL = ('{0}/_cluster/health?pretty'.format(source))
    getStatus = subprocess.Popen(['/usr/bin/curl', '-s', '-XGET', sourceURL], shell=False, stdout=subprocess.PIPE).stdout
    estatus = getStatus.read()
    statusLine = estatus.splitlines()
    status = statusLine[2].split('"')
    print "Elasticsearch status is:",status[3]

    if status[3] not in ["green","yellow"]:
        print "Elasticsearch not available"
    else:
        ## Define directories
        now = strftime("%F_%H-%M", gmtime()) 
        backupdir = ('{1}/{0}'.format(now,path))
        analyzerdir = ('{1}/{0}/analyzer'.format(now,path))
        mappingdir = ('{1}/{0}/mapping'.format(now,path))
        datadir = ('{1}/{0}/data'.format(now,path))
        ## Create directories
        print backupdir
        if not os.path.exists(backupdir):
            os.makedirs(backupdir)
        print analyzerdir
        if not os.path.exists(analyzerdir):
            os.makedirs(analyzerdir)
        print mappingdir
        if not os.path.exists(mappingdir):
            os.makedirs(mappingdir)
        print datadir
        if not os.path.exists(datadir):
            os.makedirs(datadir)
        ## Get list of indices
        indicesURL = ('{0}/_cat/indices?h=i'.format(source))
        getIndices = subprocess.Popen(['/usr/bin/curl', '-s', '-XGET', indicesURL], shell=False, stdout=subprocess.PIPE).stdout
        indices = getIndices.read()
        ## Start backup of indices
        for i in indices.splitlines():
            print strftime("%F %H:%M", gmtime()),i
            #Create 3 different backups (analyzer, mapping and data)
            print "Create analyzer backup for",i
            analyzerFile = ('{0}/{1}.json.gz'.format(analyzerdir,i))
            analyzerBackup = '/usr/local/bin/elasticdump --type=analyzer --input={0}/{1} --output=$ | /bin/gzip > {2}'.format(source,i,analyzerFile,)
            p1 = subprocess.Popen(analyzerBackup, shell=True, stdout=subprocess.PIPE)
      	    p1.wait();	
	    print "Create mapping backup for",i
	    mappingFile = ('{0}/{1}.json.gz'.format(mappingdir,i))
	    mappingBackup = '/usr/local/bin/elasticdump --type=mapping --input={0}/{1} --output=$ | /bin/gzip > {2}'.format(source,i,mappingFile,)
	    p2 = subprocess.Popen(mappingBackup, shell=True, stdout=subprocess.PIPE)
	    p2.wait();
            print "Create data backup for",i
            dataFile = ('{0}/{1}.json.gz'.format(datadir,i))
            dataBackup = '/usr/local/bin/elasticdump --type=data --input={0}/{1} --output=$ | /bin/gzip > {2}'.format(source,i,dataFile,)
            p3 = subprocess.Popen(dataBackup, shell=True, stdout=subprocess.PIPE)
            p3.wait();
def restore(path, target):
    print "Checking Elasticsearch status"
    print path
    print target

    ## Check URL
    targetURL = ('{0}/_cluster/health?pretty'.format(target))
    getStatus = subprocess.Popen(['/usr/bin/curl', '-s', '-XGET', targetURL], shell=False, stdout=subprocess.PIPE).stdout
    estatus = getStatus.read()
    statusLine = estatus.splitlines()
    status = statusLine[2].split('"')
    print "Elasticsearch status is:",status[3]

    if status[3] not in ["green","yellow"]:
        print "Elasticsearch not available"
    else:
        print "Starting Elasticsearch restore"
	restorePath = '{0}/analyzer'.format(path)
	dirList = os.listdir(restorePath)

        for i in dirList:
             print "Start import of",i
             indice = i[:-8]
             #Import Analyzer
             print "Restoring analyzer backup for",indice
             analyzerFile = '{0}/analyzer/{1}'.format(path,i)
             analyzerRestore = 'zcat {0} | /usr/local/bin/elasticdump --type=analyzer --input=$ --output={1}/{2}'.format(analyzerFile,target,indice)
             p1 = subprocess.Popen(analyzerRestore, shell=True, stdout=subprocess.PIPE)
             p1.wait();
             print "Restoring mapping backup for",indice
             mappingFile = '{0}/mapping/{1}'.format(path,i)
             mappingRestore = 'zcat {0} | /usr/local/bin/elasticdump --type=mapping --input=$ --output={1}/{2}'.format(mappingFile,target,indice)
             p2 = subprocess.Popen(mappingRestore, shell=True, stdout=subprocess.PIPE)
             p2.wait();
             print "Restoring data backup for",indice
             dataFile = '{0}/data/{1}'.format(path,i)
             dataRestore = 'zcat {0} | /usr/local/bin/elasticdump --type=data --input=$ --output={1}/{2}'.format(dataFile,target,indice)
             p3 = subprocess.Popen(dataRestore, shell=True, stdout=subprocess.PIPE)
             p3.wait();
def migrate(source, target):
    print "Start migration"

    ## Check URL Source
    sourceURL = ('{0}/_cluster/health?pretty'.format(source))
    sourceOpen = subprocess.Popen(['/usr/bin/curl', '-s', '-XGET', sourceURL], shell=False, stdout=subprocess.PIPE).stdout
    sourceRead = sourceOpen.read()
    sourceLine = sourceRead.splitlines()
    sourceStatus = sourceLine[2].split('"')
    print "Source Elasticsearch status is:",sourceStatus[3]

    ## Check URL Target
    targetURL = ('{0}/_cluster/health?pretty'.format(target))
    targetOpen = subprocess.Popen(['/usr/bin/curl', '-s', '-XGET', targetURL], shell=False, stdout=subprocess.PIPE).stdout
    targetRead = targetOpen.read()
    targetLine = targetRead.splitlines()
    targetStatus = targetLine[2].split('"')
    print "Target Elasticsearch status is:",targetStatus[3]

    if sourceStatus[3] not in ["green","yellow"]:
        print "Elasticsearch not available"
    elif targetStatus[3] not in ["green","yellow"]:
        print "Elasticsearch target not available"
    else:
        print "Start Migration"

        ## Get list of indices
        indicesURL = ('{0}/_cat/indices?h=i'.format(source))
        getIndices = subprocess.Popen(['/usr/bin/curl', '-s', '-XGET', indicesURL], shell=False, stdout=subprocess.PIPE).stdout
        indices = getIndices.read()

        for i in indices.splitlines():
             print "Start migration of",i
             #Import Analyzer
             print "Migrating analyzer for",i
             analyzerMigrate = '/usr/local/bin/elasticdump --type=analyzer --input={0}/{2} --output={1}/{2}'.format(source,target,i)
             p1 = subprocess.Popen(analyzerMigrate, shell=True, stdout=subprocess.PIPE)
             p1.wait();
             print "Migrating mapping for",i
             mappingMigrate = '/usr/local/bin/elasticdump --type=mapping --input={0}/{2} --output={1}/{2}'.format(source,target,i)
             p2 = subprocess.Popen(mappingMigrate, shell=True, stdout=subprocess.PIPE)
             p2.wait();
             print "Migrating data for",i
             dataMigrate = '/usr/local/bin/elasticdump --type=data --input={0}/{2} --output={1}/{2}'.format(source,target,i)
             p3 = subprocess.Popen(dataMigrate, shell=True, stdout=subprocess.PIPE)
             p3.wait();

if args.backup:
    if not args.source and not args.path:
        print "Require both the -u and -d arguments"
    else:
        backup(source=args.source, path=args.path)
if args.restore:
    if not args.path and not args.target:
        print "Require both the -i and -t arguments"
    else:
        restore(target=args.target, path=args.path)
if args.migrate:
    if not args.source and not args.target:
        print "Require both the --source-url and --target-url arguments"
    else:
        migrate(source=args.source,target=args.target)

