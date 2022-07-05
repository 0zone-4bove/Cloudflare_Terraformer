#!/bin/bash

echo "Zone ID: $ZONE_ID"
echo "Api Key: $API_KEY"

echo "Creating Export directory at /var/export"
mkdir /var/export

echo "Executing Python Script"
python main.py -z $ZONE_ID -a $API_KEY

# Show results (Debugging)
echo "Exporting to /var/export"
cd /var/export
pwd
ls -la 

# Run the TF Import Commands to generate the Terraform state
