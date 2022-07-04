#!/bin/bash

echo "Executing Python Script"
echo "Zone ID: $ZONE_ID"
echo "Api Key: $API_KEY"
python main.py -z $ZONE_ID -a $API_KEY

# Show results (Debugging)
ls /var/export