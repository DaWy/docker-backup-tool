import datetime, os, subprocess, docker, time, json, sys
import config
from docker.errors import ImageNotFound

client = docker.from_env()


def doBackup(cont):
    today = datetime.date.today()
    backup_name = '%s_image_%s.tar.gz' % (cont.name, today.strftime('%Y-%m-%d'))
    container_backup_name = os.path.join(config.backup_path, backup_name)
    print(' - %s ==> %s' % (cont.name, container_backup_name))
    try:
        cont.commit()
    except:
        print('    %s ==> [ERROR] Cannot commit container (backup may not contain last image changes)' % cont.name)
        pass

    os.system('docker save -o %s %s' % ('/tmp/%s.img' % cont.name, cont.image.id))
    #Compress Backup
    print(" - Compressing container %s / ID: %s" % (cont.name, cont.image.id))
    os.system('tar -czf %s /tmp/%s.img 2> /dev/null' % (container_backup_name, cont.name))


def doBackupVolumes(cont):
    today = datetime.date.today()
    command = "docker inspect -f '{{json .Mounts}}' %s" % cont.name
    volumes_json = subprocess.check_output(command, shell=True).decode(sys.stdout.encoding)
    volumes = json.loads(volumes_json)
    bind_count = 0
    for vol in volumes:
        # BIND Volumes
        if vol['Type'] == "bind":
            backup_filename = '%s_bind_%s_%s.tar.gz' % (cont.name, bind_count, today.strftime('%Y-%m-%d'))
            volume_backup_name = os.path.join(config.backup_path, backup_filename)
            print(" - Bind Volume path: %s ==> %s" % (vol['Source'], backup_filename))
            os.system('tar -czf %s %s 2> /dev/null' % (volume_backup_name, vol['Source']))
            bind_count += 1
        # Docker Volumes
        elif vol['Type'] == "volume":
            backup_filename = '%s_volume_%s_%s.tar.gz' % (cont.name, vol['Name'], today.strftime('%Y-%m-%d'))
            volume_backup_name = os.path.join(config.backup_path, backup_filename)
            print(" - Docker Volume path: %s ==> %s" % (vol['Source'], backup_filename))
            os.system('tar -czf %s %s 2> /dev/null' % (volume_backup_name, vol['Source']))

def doRestore(container_name):
    # First, check existing backups of the container
    backups_list = os.listdir(config.backup_path)
    backupeable_list = {}
    counter = 0
    for backup in backups_list:
        if backup.split('_')[1].find('image') != -1:
            b_name = backup.split('_')[0]
            backup_date = backup.split("_")[-1]
            backup_date = datetime.datetime.strptime(backup_date[0:10], "%Y-%m-%d")
            if b_name == container_name:
                #print(" -> Backup Date: %s " % backup_date.strftime("%Y-%m-%d"))
                backupeable_list[counter] = {'container': b_name, 'date':  backup_date.strftime("%Y-%m-%d"), 'filename': backup}
                #Check if we have bind volume data also, to be able to restore it        
                counter+=1
    
    for backup in backupeable_list:
        print("%s : %s" % (backup, backupeable_list[backup]))
    
    backup_id = -1
    backup_ids = list(backupeable_list.keys())
    
    while backup_id not in backup_ids:
        print(" - Select backup to restore: (%s): " % backup_ids, end="")
        backup_id = int(input())
        if backup_id not in backup_ids:
            print("[ERROR] - Incorrect backup number!")
    
    backup = backupeable_list[backup_id]
    
    print(" - Are you sure to restore this Backup? => %s (y/n): " % backup, end="")
    if input() == "y":
        print(" - OK! Restoring %s ..." % backup['container'])
        restorable_backup_path = os.path.join(config.backup_path, backup['filename'])
        backup_folder = '%s_%s' % (backup['container'], backup['date'])
        backup_restore_name = '%s:%s' % (backup['container'], backup['date'])
        # Backup decompression
        os.system('mkdir -p /tmp/%s' % backup_folder)
        os.system('cd /tmp/%s && tar -xf %s' % (backup_folder, restorable_backup_path))
        os.system('docker import /tmp/%s/tmp/%s.img %s' % (backup_folder, backup['container'], backup_restore_name))

        time.sleep(5)

        # Check restore has been succesful
        try:
            client.images.get(backup_restore_name)
            print("[OK] Docker image restored with name: %s" % backup_restore_name)
            print("[INFO] If you are using docker-compose remember to change the image field (inside docker-compose.yml) to this new image name!")
        except ImageNotFound as e:
            print("[ERROR] Docker image has not been restored. Check errors! :(")
            print(e)
        
        # Check if this backup has also volumes backed up
        bind_volumes_path = '%s_bindvolumes_%s'
        #if os.path.exists(os.path.join(config.backup_path, backup['container']))

    
    
    if len(backupeable_list) == 0:
        print("[ERROR] No backups for container: %s" % container_name)
        print(" -> List of recuperable containers: %s" % restorableContainerList())
    


def restorableContainerList():
    backups_list = os.listdir(config.backup_path)
    backupeable_list = []
    for backup in backups_list:
        if backup.split('_')[0] not in backupeable_list:
            backupeable_list.append(backup.split('_')[0])
    return backupeable_list

    

def containerNameId(cont_name):
    #print('Searching for... %s' % cont_name)
    for cont in client.containers.list("all"):
        #print("Container: %s ID: %s" % (cont.name, cont.id))
        if cont_name == cont.name:
            return cont.id



def getBackup(container_name, backup_type, month):
    backups_files = os.listdir(config.backup_path)
    founded_backups = []

    #print(container_name, backup_type, month)

    for backup in backups_files:
        backup_date = backup.split("_")[-1]
        backup_date = datetime.datetime.strptime(backup_date[0:10], "%Y-%m-%d")
        backup_name = backup.split('_')[0]
        btype = backup.split('_')[1]

        if backup_date.month == month and btype == backup_type and backup_name == container_name:
            founded_backups.append(backup)
    
    print(founded_backups)

    return founded_backups


def doClean(max_days=config.backup_max_days, containers=None):
    """
    Neteja els backups antics
    """
    deleted_backups = []

    print(" -> Deleting backups older than %s days" % max_days)

    backups_files = os.listdir(config.backup_path)
    date_now = datetime.datetime.now()

    for backup in backups_files:
        do_clean = False
        if containers != None:
            backup_name = backup.split('_')[0]
            if backup_name in containers:
                do_clean = True
        else:
            do_clean = True

        if do_clean:
            backup_date = backup.split("_")[-1]
            backup_date = datetime.datetime.strptime(backup_date[0:10], "%Y-%m-%d")
            #print("Backup: %s => Date: %s" % (backup, backup_date))

            if backup_date < (date_now - datetime.timedelta(days=max_days)):
                print(" -> Backup %s is due to delete!" % backup)
                if len(getBackup(container_name=backup.split('_')[0], backup_type=backup.split('_')[1], month=backup_date.month)) > 1:
                    print(" [!!] Deleting: %s" % backup)
                    os.remove(os.path.join(config.backup_path, backup))
                else:
                    print(" [!!] Last backup of %s Aborting delete..." % backup_date.strftime("%b"))
        

