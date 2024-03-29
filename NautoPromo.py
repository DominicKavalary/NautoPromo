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
    url = "https://IPADDRESS",
    token = "NAUTOBOT_API_TOKEN",
    verify = False
)
print("Querying")
#### GraphQL Query to Nautobot, turn to json ####
gql = nb.graphql.query(query=query)
gqljson = (json.dumps(gql.json, indent=2))

#### Parsing through each line in json for management0 address ####
## Seperate by line ##
gqljsonlines = gqljson.split('\n')

## Create empty array to be filled with target addresses, and set flags for if the management0 interface and address had been found ##
arrayOfTargets = []
managementFound = False
addressFound = False
address = ""

## Go through lines, when the management0 flag is set to true, the next address it finds will be considered Management0's. when it finds both, append a target to the list with ocprometheus default exposed port of 8080. ##
for line in gqljsonlines:
#   print(line) uncomment to see every line returned in query. Another idea would be to export it as a document to read later
   if '"name": "Management0"' in line and managementFound == False:
       managementFound = True
   elif '"address"' in line and addressFound == False:
       address = line[line.find(":")+3:line.find("/")]
       addressFound = True
   if managementFound and addressFound:
       arrayOfTargets.append(address+":8080")
       managementFound = False
       addressFound = False
       address = ""
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
