#!/bin/bash

echo "Zone ID: $ZONE_ID"
echo "Api Key: $API_KEY"

echo "Creating Export directory at /var/export"
mkdir /var/export

echo "Executing Python Script"
python main.py -z $ZONE_ID -a $API_KEY

# Show results (Debugging)
ls /var/export