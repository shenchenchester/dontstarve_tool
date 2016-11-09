## dontstarve_tool
A tool for Don't Starve Together, backup, read and restore game saves
# Features
Periodical backup, save your ass any time
Easy restore, get back to life in a breeze
Limited backups, don't worry about growing disk usage
Modification detection, won't flush away your backups when taking a break

# Dependency
Python 2.7
# Config
Edit backup.py,
SAVE_DIR is the game's save location
BACKUP_DIR is your backup location
INTERVAL stands for seconds between each backup check
MAX_BACKUPS is the limit of backups
# How to run
For Windows user, click backup.bat and run
For UNIX user, run "python backup.py" in shell
- Backup
Run the tool, leave it there, and then enjoy your game
- Restore
Exit the game, run the tool and select one of your backups to restore,
then restart the game.
