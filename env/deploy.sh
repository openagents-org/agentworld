#!/bin/bash

# Define source and destination
SOURCE_DIR="$(pwd)"
DESTINATION="root@172.232.187.238:/root/services/kaetram"

echo "Deploying Kaetram to production server..."

# Use rsync to upload files, excluding node_modules
rsync -avz --progress \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude '.DS_Store' \
  --exclude 'package.json' \
  "$SOURCE_DIR/" "$DESTINATION"

# Check if rsync was successful
if [ $? -eq 0 ]; then
  echo "Deployment completed successfully!"
else
  echo "Deployment failed. Please check your connection and try again."
  exit 1
fi
