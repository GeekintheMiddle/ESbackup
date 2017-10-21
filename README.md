# ESbackup
Backup/Restore/Migration tool for Elasticsearch

This tool will help to create compressed elasticsearch backups and restores.

This tool is based on elasticdump. Credits to the builders of elasticdump. https://github.com/taskrabbit/elasticsearch-dump

### How to install

```
apt-get install npm
npm install elasticdump -g
ln -s /usr/bin/nodejs /usr/bin/node
git clone https://github.com/GeekintheMiddle/esbackup.git
cd esbackup
cp esbackup.py /usr/local/bin/esbackup
```

### How to use

```
usage: esbackup [-h] [--backup] [--restore] [--migrate] [-u SOURCE] [-d PATH]
                [-i IMPORT] [-t TARGET]

Elasticsearch Backup/Restore script.

optional arguments:
  -h, --help  show this help message and exit
  --backup    ...
  --restore   ...
  --migrate   ...
  -u SOURCE   Source Elasticsearch URL
  -d PATH     Backup Data Directory
  -i IMPORT   Import Data Directory
  -t TARGET   Target Elasticsearch URL
```

### Examples

```
# Backup elasticsearch data
esbackup --backup -u http://127.0.0.1:9200 -d /home/backupuser/esbackup

# Restore elasticsearch data from folder
esbackup --restore -t http://127.0.0.1:9200 -d /home/backupuser/esbackup/2017-10-21_11-07

# Migrate from elaticsearch cluster to another cluster 
esbackup --migrate -u http://127.0.0.1:9200 -t http://123.123.123.123:9200
```

## Authors

* **Sven Mollinga** - [GeekintheMiddle](https://www.geekinthemiddle.com)

## Sources ##

* Elasticdump [https://github.com/taskrabbit/elasticsearch-dump]

