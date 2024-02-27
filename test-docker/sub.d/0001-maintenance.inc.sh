#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------

BACKUP_DIR=${SERVER_DIR}/backups

#-------------------------------------------------------------------------------
# Maintenance
#-------------------------------------------------------------------------------

function backup() {
  ARCHIVE=${BACKUP_DIR}/palworld-save-`date +%Y-%m-%d_%H-%M-%S`.tar.gz
  mkdir -p ${BACKUP_DIR}
  tar -cvzf ${ARCHIVE} --exclude=Crash* -C ${PAL_DIR} Saved
}

function restore() {
  if [ "$1" = "" -o ! -f "$1" ]; then
    echo "backup file '$1' does not found."
    exit 1
  fi
  rm -rf ${PAL_DIR}/Saved.old
  mv ${PAL_DIR}/Saved ${PAL_DIR}/Saved.old
  tar -xvzf $1 -C ${PAL_DIR}
}

#-------------------------------------------------------------------------------
# Sub Commands
#-------------------------------------------------------------------------------
USAGE="${USAGE}
  ---( maintenance )---
  backup            ... make backup
  restore <file>    ... restore backup
"

case ${ARGV[0]} in
"backup")
  needStop && backup
  exit 0
  ;;
"restore")
  needStop && restore ${ARGV[1]}
  exit 0
  ;;
esac
