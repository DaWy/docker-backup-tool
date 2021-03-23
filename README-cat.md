# docker-backups

Eina per administrar Backups de Contenidors Docker.

## Explicació

Aquesta eina realitza backups dels contenidors de Docker + els volumns que el contenidor tingui asociat. També permet restaurar backups en nous contenidors!*


## Requisits

* Python 3.7
* Debian

## Instal·lació

1. Clonem Repo (hem de tenir claus SSH Copiades!)

`git clone https://github.com/DaWy/docker-backup-tool`

2. (Opcional) Si volem que la comanda docker-backup estigui disponible system-wide, executem el següent:

`sudo ln -s <DIRETORI_DEL_PROJETE_CLONAT>/docker-backup.py /usr/bin/docker-backup`

Aixó crearà un enllaç simbólic al /usr/bin que ens permetra executar **docker-backup** desde qualsevol lloc al sistema

## Configuració

En el config.py hi podem configurar el path de destí per defecte i algunes coses més!

* **backup_path** -> Path de destí dels backups (o d'origen si volem restaurar)
* **excluded_containers** -> Containers exclosos dels backups. Aquets contenidors no s'els tindra en compte amb la comanda -a (--all) a l'hora de fer backups
* **backup_max_days** -> Maxim dies de retenció de backups. Quan la data del backup sigui inferior a la data actual - aquest valor, els backups anteriors seran eliminats (quan s'executi el mode -cl (--clean)) conservant només 1 backup mensual. 

## Ús 

Podem veure les diferents opcions de l'script fent servir el parametre -h / --help

`./docker-backup.py --help`

Les principals opcions son:

### Backup d'un contenidor. 

Si en volem fer mes d'un a la vegada, podem separar els noms amb ,

* `./docker.backup.py -b -c [LLISTA_CONTENIDORS]`

Exemple:

* `./docker-backup.py -b -c glpi phpmyadmin`

Podem definir el directori de destí amb -d. Exemple si volem que els backups es crein a /backup:

* `./docker-backup.py -b -c glpi -d /backups`

### Neteja backups antics

En el config.py podem definir el maxim de dies de conservació de backups. 
Si executem:

`./docker-backup.py -cl [OPIONAL: NOM_CONTENIDOR]`

Netejarà tots els backups anteriors als dies indicats en l'arxiu. Conservarà només 1 backup de cada contenidor per nom.
Podem indicar que neteji nomes 1 backup o tots. Exemples:

* Netejar nomes un backup: 

`./docker-backup.py -cl -c glpi-mm`

* Netejar TOTS els backups

`./docker-backup.py -cl`


### Restaurar backups

Podem restaurar una imatge d'un backup de la següent manera:

`./docker-backup -r -c glpi-mm`

L'script consultarà els backups dins del **backup_path** (indicat al config.py o el indicat amb el paràmetre -d) i ens demanará quin dels backups disponibles volem restaurar.

Indiquem el backup amb el número y la imatge quedara restaurada en el daemon local de docker. 

La imatge tindrà el nom de <NOM_CONTENIDOR:DATA_BACKUP> per a que la poguem localitzar. Despres només faltaria indicar en el contenidor que ens interessi que estiri aquesta imatge. 

### Restaurar dades dels volums

***Funció per implementar*
