import pynautobot
import json

query = """
query {
  devices {
    device_type{
      model
    }
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
print("Started, making API call")
nb = pynautobot.api(
    url="https://10.128.0.8",
    token="41ddbd050e13bd939fb266adcc5ecf20a24034fd",
    verify=False
)
gql = nb.graphql.query(query=query)

gqljson = (json.dumps(gql.json, indent=2))
print("parsing through request for 172. addresses")
gqljsonlines = gqljson.split('\n')
arrayOfAddresses = []
complete = False
while complete == False:
    name = ""
    address = ""
    model = ""
    for line in gqljsonlines:
        print(line)
        if "model" in line and model == "":
            model = line[line.find(":")+3:len(line)-2]
        elif "name" in line and name == "":
            name = line[line.find(":")+3:len(line)-2]
        elif "172." in line and address == "":
            address = line[line.find(":")+3:line.find("/")]
        if model != "" and name != "" and address != "":
            arrayOfAddresses.append(address+":8080")
            name = ""
            address = ""
            model = ""
            complete = True
print("creating prometheus targets list based on query")
prometheusTargets = "- targets: ["
for object in arrayOfAddresses:
  prometheusTargets = prometheusTargets + "'" + object + "', "
prometheusTargets = prometheusTargets[:-2]
prometheusTargets = prometheusTargets + "]"
print("current list of targets:")
print(prometheusTargets)
writeOver = False
print("reading target file")
with open("/home/NautoPromo/NautobotTargets.yml", "r") as file:
  for line in file:
    print("target file:")
    print(line)
    if line != prometheusTargets:
      print("target file differs from current list")
      writeOver = True
if writeOver:
  print("writing over file")
  with open("/home/NautoPromo/NautobotTargets.yml", "w") as file:
    file.write(prometheusTargets)
else:
  print("no differences found, no changes made to target file")
