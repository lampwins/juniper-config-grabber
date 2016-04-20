from Configuration import Configuration
from Vlan import Vlan
import re
import getpass

host = raw_input("Host: ")
user = raw_input("Username: ")
password = getpass.getpass()

device = Configuration(host, user, password, ["vlans", "interfaces"])

vlan_names = device.get_filtered_lines("vlans", ["vlan-id"], [])

vlans = []
for line in vlan_names:
    line = line.strip('\n')
    line = line.rstrip()
    m = re.search('vlans (.+?) ', line)
    vlan_name = m.group(1)
    m = re.search('vlan-id (.*)', line)
    vlan_id = m.group(1)
    vlan_description_line = device.get_filtered_lines("vlans", [vlan_name, "description"], [])
    if len(vlan_description_line) > 0:
        m = re.search('description (.*)', vlan_description_line[0])
        vlan_description = m.group(1)
    else:
        vlan_description = None

    vlan_address_line = device.get_filtered_lines("interfaces", ["unit " + vlan_id + " ", "address"], [])
    if len(vlan_address_line) > 0:
        print vlan_address_line[0]
        m = re.search('address (([0-9]{1,3}\.?){4}(/[0-9]{1,2})?)', vlan_address_line[0])
        vlan_address = m.group(1)
    else:
        vlan_address = None

    vlans.append(Vlan(vlan_name, vlan_id, vlan_description, vlan_address))


for vlan in vlans:
    print vlan.name + " " + vlan.id + " " + vlan.description + " " + vlan.address

