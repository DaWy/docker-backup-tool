# App Name
app_name = 'Docker Backup & Restore TOOL'

# Path where the backups files goes
backup_path = ""

# List of containers that will be excluded from --all backup
excluded_containers = ['portainer', 'watchtower']

# Older backup than specified days here will be deleted.
# Only first backup of the month will be saved
backup_max_days = 60