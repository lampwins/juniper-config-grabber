import getpass
import re
from Configuration import Configuration
from Device import Device
from Vlan import Vlan
import packetlogic2

user = raw_input("Username: ")
password = getpass.getpass()

devices = []
with open("devices.txt") as file:
    for line in file:
        line = line.strip("\n")
        device_config = Configuration(line, user, password, ["vlans", "interfaces", "system"])
        hostname_line = device_config.get_filtered_lines("system", ["host-name"], [])
        m = re.search('host-name (.*)', hostname_line[0])
        device_hostname = m.group(1)
        devices.append(Device(line, device_hostname, device_config))

for device in devices:
    vlan_names = device.config.get_filtered_lines("vlans", ["vlan-id"], [])
    vlans = []
    for line in vlan_names:
        m = re.search('vlans (.+?) ', line)
        vlan_name = m.group(1)
        m = re.search('vlan-id (.*)', line)
        vlan_id = m.group(1)
        vlan_description_line = device.config.get_filtered_lines("vlans", [vlan_name, "description"], [])
        if len(vlan_description_line) > 0:
            m = re.search('description (.*)', vlan_description_line[0])
            vlan_description = m.group(1)
        else:
            vlan_description = None
        vlan_address_lines = device.config.get_filtered_lines("interfaces", ["unit " + vlan_id + " ", "address"], ["preferred"])
        if len(vlan_address_lines) > 0:
            for vlan_address_line in vlan_address_lines:
                m = re.search('address (([0-9]{1,3}\.?){4}(/[0-9]{1,2})?)', vlan_address_line)
                vlan_address = m.group(1)
                if vlan_description is None:
                    vlan_interface_description_line = device.config.get_filtered_lines("interfaces", ["unit " + vlan_id + " ", "description"], [])
                    if len(vlan_interface_description_line) > 0:
                        m = re.search('description (.*)', vlan_interface_description_line[0])
                        vlan_description = m.group(1)
                    else:
                        vlan_description = ""
                if "153.9." in vlan_address:
                    if "de" in vlan_description:
                        vlan_description = vlan_description[:-2]
                    vlans.append(Vlan(vlan_name, vlan_id, vlan_description, vlan_address))
    device.set_vlans(vlans)

for device in devices:
    print device.name
    for vlan in device.vlans:
        print "\t" + vlan.name + " " + vlan.id + " " + vlan.description + " " + vlan.address

pl = packetlogic2.connect("10.254.29.11", user, password)
r = pl.Ruleset()

for device in devices:
    device_obj_name = device.name + "no"
    obj = r.object_get('/NetObjects/' + device_obj_name)
    if not obj:
        r.object_add('/NetObjects/' + device_obj_name)
        obj = r.object_get('/NetObjects/' + device_obj_name)
    for vlan in device.vlans:
        vlan_obj_name = vlan.name + "_" + vlan.description + "no"
        vlan_obj = r.object_get('/NetObjects/' + device_obj_name + "/" + vlan_obj_name)
        if not vlan_obj:
            r.object_add('/NetObjects/' + device_obj_name + "/" + vlan_obj_name)
            vlan_obj = vlan_obj = r.object_get('/NetObjects/' + device_obj_name + "/" + vlan_obj_name)
        if vlan.address not in vlan_obj.items:
            vlan_obj.add(vlan.address)
#for device in devices:
#    obj = r.object_get('/NetObjects/VOIP_NETWORKSno')
#    for vlan in device.vlans:
#        if vlan.address not in obj.items:
#            obj.add(vlan.address)

r.commit()
