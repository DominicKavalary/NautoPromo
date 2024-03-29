#### Imports ####
import pynautobot
import json

#### Query to Nautobot for list of Management0 addresses ####
query = """
query {
  devices {
    name
    interfaces {
      name
      ip_addresses {
        address
      }
    }
  }
}
"""

#### Nautobot API Connection stuff. verify=False for self signed certs ###
nb = pynautobot.api(
    url = "https://IP_ADDRESS",
    token = "API_NAUTOBOT_TOKEN",
    verify = False
)
print("Querying")
#### GraphQL Query to Nautobot, turn to json ####
gql = nb.graphql.query(query=query)
gqljson = (json.dumps(gql.json, indent=2))
data = json.loads(gqljson)
#### Parsing through each line in json for management0 address ####

## Create empty array to be filled with target addresses ##
arrayOfTargets = []

## iterate through the json data with the keys and values to obtain ip addresses
for device in data['data']['devices']:
  for interface in device['interfaces']:
    if interface['name'] == 'Management0':
      for ip_address in interface['ip_addresses']:
         address = ip_address['address']
         address = address[:address.find("/")]
         arrayOfTargets.append(address+":8080")

# an idea could be to also have it run through a blacklist file and remove any non wanted devices. could be useful if you need to take a device down for a while #

#### Create a string that has the one line of yaml that the file_sd_config target file needs. basically, "- targets:" and then a string array of the targets+port ####
prometheusTargets = "- targets: ["
for target in arrayOfTargets:
  prometheusTargets = prometheusTargets + "'" + target + "', "
prometheusTargets = prometheusTargets[:-2]
prometheusTargets = prometheusTargets + "]"
print(f"Targets found:\n{prometheusTargets}")

#### Read target file on machine, if it has not changed, do not write over it, if it has, write over it ####
writeOver = False
with open("/home/NautoPromo/NautobotTargets.yml", "r") as targetFile:
  for line in targetFile:
    if line != prometheusTargets:
      writeOver = True
if writeOver:
  with open("/home/NautoPromo/NautobotTargets.yml", "w") as file:
    file.write(prometheusTargets)
else:
  print("no differences found since last query, no changes made to target file")
