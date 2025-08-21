#!/usr/bin/env bash
#
# deploy.sh
#
# Copies the contents of /home/developer/proyectos/osigris to the EC2 instance,
# excluding any files or folders matching patterns in .gitignore.
#
# Usage: ./deploy.sh
# (Assumes .gitignore lives at /home/developer/proyectos/osigris/.gitignore.)

# 1) Configuration: adjust these if needed.
SSH_KEY="rqagro.pem"
SOURCE_DIR="/home/developer/proyectos/osigris/"
GITIGNORE_FILE="${SOURCE_DIR}.gitignore"

DEST_USER="ubuntu"
DEST_HOST="ec2-18-100-110-120.eu-south-2.compute.amazonaws.com"
DEST_DIR="/home/ubuntu/v2/"

# 2) Sanity checks
if [ ! -f "${SSH_KEY}" ]; then
  echo "ERROR: SSH key not found at ${SSH_KEY}"
  exit 1
fi

if [ ! -d "${SOURCE_DIR}" ]; then
  echo "ERROR: Source directory not found: ${SOURCE_DIR}"
  exit 1
fi

if [ ! -f "${GITIGNORE_FILE}" ]; then
  echo "WARNING: No .gitignore found at ${GITIGNORE_FILE}. All files will be copied."
fi

# 3) Run rsync:
#
#    -a       : archive mode (preserves permissions, timestamps, symbolic links, etc.)
#    -v       : verbose output
#    -z       : compress file data during the transfer
#    --delete : delete files on the destination that no longer exist in the source
#               (optional; uncomment if you want a mirror, but be careful)
#    --exclude-from="${GITIGNORE_FILE}"
#             : reads ignore‐patterns from .gitignore and excludes matching files
#    -e "ssh -i \"${SSH_KEY}\""
#             : tells rsync to use ssh with your private key
#
#    Note: By specifying SOURCE_DIR with a trailing slash (…/osigris/), rsync will copy
#          *contents* of osigris into DEST_DIR. If you omit the trailing slash, rsync
#          would create /home/ubuntu/osigris/osigris/ instead.
#
rsync -avz \
  --exclude-from="${GITIGNORE_FILE}" \
  -e "ssh -i \"${SSH_KEY}\"" \
  "${SOURCE_DIR}" \
  "${DEST_USER}@${DEST_HOST}:${DEST_DIR}"

# If you prefer to delete remote files that were removed locally, uncomment the next line:
# rsync -avz --delete --exclude-from="${GITIGNORE_FILE}" -e "ssh -i \"${SSH_KEY}\"" "${SOURCE_DIR}" "${DEST_USER}@${DEST_HOST}:${DEST_DIR}"

exit 0
