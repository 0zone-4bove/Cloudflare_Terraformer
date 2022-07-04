# Cloudflare_Terraformer

# Premise
This is a small project I started because my company managed so many DNS records in Cloudflare, yet none of them were in Terraform code. I wanted a program that would be able to generate both Terraform code for the DNS records, and the associated Terraform import commands so that one could have a Terraform state.

# How to run

## Python Standalone
python main.py -z {ZONE_ID} -a {API_KEY}

## Docker
``` bash
export API_KEY="{Your API Key}"
export ZONE_ID="{Your Zone ID}"
docker run -i -e API_KEY -e ZONE_ID --mount source=exported_terraform,target=/var/export cloudflare_terraformer:latest 
```


## Docker Compose
```YAML
version: "3.9"
   
services:
  cloudflare_terraformer:
    image: cloudflare_terraformer:latest
    volumes:
      - ./export:/var/export
    environment:
      - API_KEY={FILL_ME}
      - ZONE_ID={FILL_ME}
```