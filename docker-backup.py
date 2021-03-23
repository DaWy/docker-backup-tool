#!/usr/bin/python3.7
import docker, os, datetime, subprocess, argparse
from functions import doBackup, containerNameId, doClean, doRestore, doBackupVolumes
import config
client = docker.from_env()

invalid_containers = []

print('### Docker Backup & Restore TOOL ###')
print('Tool made by: David Martin (@daweiii / masterplanelles@gmail.com)')

menu = argparse.ArgumentParser(description="Docker Backup Tool", )
menu_containers = menu.add_mutually_exclusive_group()
menu_containers.add_argument('-c', '--containers', metavar='container_name', type=str, nargs='+',
                    help='Containers to backup (separated by space)')
menu_containers.add_argument('-a', '--all', action="store_true", help='Backup ALL containers, excluding the excluded ones in config')

menu_action = menu.add_mutually_exclusive_group()
menu_action.add_argument('-b', '--backup', action="store_true", help='Do Backups!')
menu_action.add_argument('-cl', '--clean', action="store_true", help='Clean OLD Backups - WARNING: THIS WILL DELETE BACKUPS. PLEASE CARE, RTFM!!!')
menu_action.add_argument('-r', '--restore', action="store_true", help='Restore Backups to a new Container')

menu_directory = menu.add_mutually_exclusive_group()
menu_directory.add_argument('-d', '--directory', help='Set destination directory. If not defined, will be using default in config.py. Must be an existing directory!')

args = menu.parse_args()

# Initial Checks
if args.directory != None:
    config.backup_path = args.directory
if os.path.exists(config.backup_path) and config.backup_path.find("/tmp") == -1:
    print('[OK] Backup path set and exists: %s' % config.backup_path)
else:
    print('[ERROR] Backup path does not exists or is not allowed!! (/tmp) Check destination path!! :(')
    exit()


# Actions (Clean, Backup and Restore)
if args.clean:
    print('[CLEAN BACKUPS]')
    doClean(containers=args.containers)
elif args.backup:
    if args.containers is None and args.all is None:
        menu.print_help()
        exit()
    elif args.all is None:
        included_containers = args.containers
    print('[BACKUP CONTAINERS]')

    # If all containers, then set it:
    included_containers = []
    for cont in client.containers.list("all"):
        included_containers.append(cont.name)

    # Check defined containers do exist
    for container in included_containers:
        container_id = containerNameId(container)
        if container_id is not None:
            if client.containers.get(container_id) in client.containers.list("all"):
                pass
            else:
                invalid_containers.append(container)
            
        else:
            invalid_containers.append(container)


    if len(invalid_containers) > 0:
        print('[ERROR] The following containers does not exist. Please check containers names!')
        print(' -- %s' % invalid_containers)
        exit()


    # Backup
    
    print('> BACKUP START <')
    for cont in client.containers.list("all"):
        if cont.name in included_containers and cont.name not in config.excluded_containers:
            print(" --> Backing up: %s" % cont.name)
            print(" - Stoping: %s" % cont.name)
            client.containers.get(cont.id).stop()
            
            # Backup Container
            print(" - Backing up container image...")
            doBackup(cont)
            # Backup Volumes
            print(" - Backing up container volumes...")
            doBackupVolumes(cont)
            print(" --> Backup done! Starting again %s" % cont.name)
            client.containers.get(cont.id).start()
        elif cont.name in config.excluded_containers:
            print(" !! Container %s is on excluded containers list! Ignoring..." % cont.name)
        else:
            pass
    

    # Prune unused Images (the ones we make for the backup) to avoid getting out of free space
    print('> Pruning unused images <')
    os.system('docker image prune -a -f')

    # Eliminar imatges del /tmp
    print('> Deleting backup /tmp/ Images <')
    os.system('rm /tmp/*.img 2> /dev/null')

elif args.restore:
    print('[RESTORE CONTAINERS]')
    if args.containers is None:
        print('[ERROR] -> Not container specified! :(')
        exit()
    doRestore(args.containers[0])
    exit()
else:
    print('[ERROR] No action selected!')
    menu.print_help()
    exit()

print('### BACKUP SCRIPT END! :) ###')








    

