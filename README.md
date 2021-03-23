# docker-backups

Tool for managing a Docker Container server Backups

## Details

This tool make backups of the Docker Containers (the image itself) + associated volumes. It also allows to restore any backup to a new Container!
It also bakcup Bind Volumes + Regular docker volumes


## Requirements

* Python 3.7
* Debian (or any Distro that is compatible with Python and docker python lib) 

It could be compatible with WSL2 (windows subsystem for Linux) but has not been tested

## Setup

1. Clone the Repo

`git clone https://github.com/DaWy/docker-backup-tool`

2. (Optional) If you want to make the docker-backup command systemwide, do this:

`sudo ln -s docker-backup-tool/docker-backup.py /usr/bin/docker-backup`

That will create a symbolic link to /usr/bin that will allow us execute docker-backup from any path on this system

## Config

We can setup some things in the config.py file, like backup destination folder.

* **backup_path** -> Destination backup folder (also its source folder if we want to restore some backup)
* **excluded_containers** -> Excluded containers. This containers will be ignored when using the --all flag
* **backup_max_days** -> Max retention backup days. When a backup reach max days old, it will be deleted (when issuing the clean command) 

## Usage

We can show the script options by issuing the -h / --help parameter

`./docker-backup.py --help`

Principal options:

### Container backup

If we want to backup more than one container at once, we can issue all the containers separated by semicolon (,)

* `./docker.backup.py -c [CONTAINER_LIST]`

Example:

* `./docker-backup.py -c glpi phpmyadmin`

We can set the destination folder (of the backup) with the -d parameter. Example, backing up containers to /backup folder:

* `./docker-backup.py -c glpi -d /backups`

### Old backups clean

We can set the max retention backup days on the config.py (as shown above)

`./docker-backup.py -cl [OPTIONAL: CONTAINER_NAME]`

That will clean all of the backups that are older in days than the number we specified in the config.py. It will always NOT DELETE at least ONE backup for MONTH

We can just clean ONE container backups, for example:

`./docker-backup.py -cl -c glpi-mm`

Or we can clean ALL the backups:

`./docker-backup.py -cl`


### Container restoration

We can restore a container image from a backup by this way:

`./docker-backup -r -c glpi-mm`

Script will check backups inside the **backup_path** folder (or folder set with -d) and will prompt us wich of the backups we wish to restore

We just write the backup number and the container image will be restore to the local docker Daemon

The resultant restored image will have this name: <CONTAINER_NAME:BACKUP_DATE> to be able to be located. After this, we could just assing this image to some container.

### Volume restore

NYR
