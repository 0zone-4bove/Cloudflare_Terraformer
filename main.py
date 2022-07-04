# Imports
import json
import io
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
import requests
import argparse

# ===================== Arg Parsing =====================

parser = argparse.ArgumentParser()
parser.add_argument("-z",
                    "--zone-id",
                    help="Cloudflare Zone (Domain)")
parser.add_argument("-a",
                    "--api-key",
                    help="Cloudflare API key needed to access the account")

args = parser.parse_args()

# Arg checking
if args.zone_id is None:
    print(f"Missing Zone ID argument! Exiting...")
    exit()
if args.api_key is None:
    print(f"Missing API Key! Exiting...")
    exit()

# Vars
zone_ID = args.zone_id
api_Key = args.api_key

# Static Vars ( Don't change! )
content_type = "application/json"
per_page = 1000
tf_import_commands = "terraform init \n"

# ===================== File Import =====================

print(f"Working out of {os.getcwd()}")

# Header Location
header_file = "tf_header.j2"
# File Check
if not os.path.exists(header_file):
    print("Header file does not exist! Exiting....")
    exit(code=200)
# Get the contents of the header
template_export = open(header_file, "r").read()

# Template Location
template_file = "tf_template.j2"
# File Check
if not os.path.exists(template_file):
    print("Template file does not exist! Exiting....")
    exit(code=200)

# Vars Location
vars_file = "tf_vars.j2"
# File Check
if not os.path.exists(vars_file):
    print("Vars file does not exist! Exiting....")
    exit(code=200)
# Get the contents of the vars file
vars_export = open(vars_file, "r").read()

# ===================== Jinja Setup =====================
# Tell the loader to search in the running folder
fs_loader = FileSystemLoader(searchpath=f".{os.sep}")
# Create the Environment
env = Environment(loader=fs_loader, autoescape=select_autoescape(['xml']))
# Load the template file
template = env.get_template(template_file)
# Load the vars template file
vars_template = env.get_template(vars_file)

# ===================== API Calls =====================

# Declare Headers
request_headers = {
    "Authorization": "Bearer " + api_Key,
    "Content-Type": content_type
}

# Get CloudFlare Info from their API
print(f"Requesting Info from CloudFlare API for zone {zone_ID}")
response = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_ID}",headers = request_headers)
cloudflare_info = json.loads(response.text)
print(f"Response Length: {len(response.text)}")


# ===================== Parse CloudFlare Info =====================

# Convert to JSON String
cf_info_json = json.dumps(cloudflare_info['result'], indent = 4)

# Get Domain Info
parent_domain = cloudflare_info['result']['name']
account_id = cloudflare_info['result']['account']['id']

var_dict = {
    "account_id" : account_id,
    "zone_id" : zone_ID
}

# ===================== Template Files =====================

# Save the vars.tf file
with open(f'export{os.sep}vars.tf', 'w') as vars_file_w:   
    vars_file_w.write(vars_template.render(vars=var_dict))
  

# Save the Cloudflare results
with open(f'export{os.sep}cf_info.json', 'w') as cf_Info_File:   
    cf_Info_File.write(cf_info_json)
    
# ===================== Requesting DNS Records =====================

# Get DNS Records from their API as well
print(f"Requesting DNS Records from CloudFlare API for zone {zone_ID}")
response = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_ID}/dns_records?per_page={per_page}",headers = request_headers)
print(f"Response Length: {len(response.text)}")

# JSON result set
result_json = json.loads(response.text)
# print(dns_records)

# Result array of JSON values
records = result_json["result"]

# ===================== Parsing DNS Records =====================

# Loop through records
print(f"Parsing {len(records)} records...")
for rec in records:
    # print(f"{rec}")

    # Zone 
    zone_Name = rec['zone_name']
    
    # DNS record
    rec_id = rec['id']
    rec_name = rec['name']
    rec_type = rec['type']
    rec_content = rec['content']
    rec_subdomain = rec_name.split('.')[0]
    rec_proxied = rec['proxied']
    rec_ttl = rec['ttl']

    # Terraform Related
    resource_name = f"{parent_domain.replace('.', '_')}_{rec_type}_{rec_subdomain}"

    # Create the entry
    entry = {
        "DOMAIN" : parent_domain,
        "NAME" : rec_subdomain,
        "TYPE" : rec_type,
        "VALUE" : rec_content,
        "TTL" : rec_ttl,
        "PROXIED" : rec_proxied,
        # Build the Resource name
        "RESOURCE_NAME" : resource_name
    }
    # Use the Entry object to populate the template
    TF_Entry = template.render(entry=entry)

    # Add this entry to the template
    template_export += TF_Entry

    # Build TF Import Commands
    tf_import_commands += f"terraform import cloudflare_record.{resource_name} {zone_ID}/{rec_id}\n"


# Adding a pause to the end of the imports
tf_import_commands += "pause"

# ===================== Exporting Terraform and Powershell Files =====================

# Save all of the Terraform resources
print(f"Saving main.tf")
with open(f'export{os.sep}main.tf', 'w') as cf_main_file:   
    cf_main_file.write(template_export) 

# Now we generate the terraform import commands
print(f"Saving tf_imports.ps1")
with open(f'export{os.sep}tf_imports.ps1', 'w') as tf_import_file:   
    tf_import_file.write(tf_import_commands) 

