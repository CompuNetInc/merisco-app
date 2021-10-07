import sys
from getpass import getpass
import json
import logging
import argparse
import re
import asyncio

import yaml
from scrapli import Scrapli
from scrapli import AsyncScrapli
from scrapli.driver.core import AsyncIOSXEDriver
from scrapli.helper import textfsm_parse

from g_apis import meraki_api as meraki


logging.basicConfig(filename="scrapli.log", level=logging.WARNING)


def load_yaml(filename):
    try:
        with open(filename) as _:
            return yaml.load(_, Loader=yaml.SafeLoader)
    except:
        print("Invalid device file!")
        sys.exit(0)


def create_json_file(filename: str, data):
    with open(filename, 'a') as fout:
        fout.write(json.dumps(data, indent=4))


def lulu_stuff():
    
    grab_org_id()
    grab_list_of_networks(orgid)
    await grab_list_of_devices_from_networks(orgid, network)
    await grab_port_configs(serial)
    await grab_port_statuses(serial, ports)

    grab_cisco_ports_statuses()
    
    output_stuff()


def meraki_stuff(api_key: str, orgid: str, serial: str):

    # Create/test connection with Meraki as 'mydashboard'
    mydashboard = meraki(api_key)

    if not orgid:
        orgid = input("Org ID: ")
    if not serial:
        serial = input("Serial: ")

    # Grab Organizations
    orgs = mydashboard.get_organizations()

    print(f"Orgs = \n\n {orgs}")

    # Grab Networks
    networks = mydashboard.get_networks(int(orgid))

    print(f"Networks = \n\n {networks}")

    # Grab Switch port status
    statuses = mydashboard.get_switch_ports_status(serial)

    print(f"Statuses = \n\n {statuses}")

    # Grab Switch port status individual port
    portconfig = mydashboard.get_switch_ports_config(serial)
    port2config = mydashboard.get_switch_ports_config(serial, "2")

    print(f"\n\nPorts config = \n\n {portconfig}")
    print(f"\n\nPort 2 config = \n\n {port2config}")

    create_json_file("statuses.json",statuses)
    create_json_file("portconfigs.json",portconfig)


def scrapli_stuff(MY_DEVICE: dict):
    with Scrapli(**MY_DEVICE) as conn:
        print(conn.get_prompt())
        test = conn.send_command("show ip interface brief")
        print(test.textfsm_parse_output())
        print(f"\n\n{test.channel_input}")

        commands = ["show version", "show run | sec bgp"]
        test2 = conn.send_commands(commands)
        print(dir(test2))
        print(test2.result)
        print("\n\nhi\n\n")
        print(test2)
        for i in test2:
            print(i)
        print(test2[0].result)

        test3 = conn.send_command("show interfaces status") # NOTE: DOESN'T WORK ON ROUTERS (not a command)
        
        result_textfsm= textfsm_parse("cisco_ios_show_interfaces_status_physical_only.textfsm", test3.result)
        print(result_textfsm)
        print("\n\nhere we go\n\n")
        print(test3.textfsm_parse_output())

        # Create to compare
        create_json_file("customtextfsm.json", result_textfsm)
        create_json_file("ntctextfsm.json", test3.textfsm_parse_output())


async def async_scrapli_stuff(device: dict):
    try:
        conn = AsyncIOSXEDriver(**device)
        await conn.open()
        prompt = await conn.get_prompt()
        version = await conn.send_command("show version")
        await conn.close()
        
        return (prompt, version)

    except Exception as e:
        print(e)
        # if "No matching cipher" in repr(e):
        #     cipher = re.search(r'(?<=their offer: )(.+?)(?=,)', repr(e)).group(1)
        #     logging.warning(f"Retrying connection to {host} with new cipher: {cipher}")
        #     MY_DEVICE["transport_options"] = {"open_cmd": ["-c", cipher]}


def cisco_connect(host: str):
    MY_DEVICE = {
        "host": host,
        "auth_username": username,
        "auth_password": password,
        "auth_strict_key": False,
        "platform": "cisco_iosxe",
    }
    print(MY_DEVICE)
    try:
        scrapli_stuff(MY_DEVICE)
    except Exception as e:
        if "No matching cipher" in repr(e):
            cipher = re.search(r'(?<=their offer: )(.+?)(?=,)', repr(e)).group(1)
            logging.warning(f"Retrying connection to {host} with new cipher: {cipher}")
            MY_DEVICE["transport_options"] = {"open_cmd": ["-c", cipher]}
            scrapli_stuff(MY_DEVICE)

def cisco_stuff(username: str, password: str, filename: str):

    devices = load_yaml(filename)
    print(devices)

    for host in devices["IOS"]:
        cisco_connect(host)


async def async_cisco_stuff(username: str, password: str, filename: str):

    devices = load_yaml(filename)
    print(devices)
    MY_DEVICES = []
    
    # Build list of devices
    for host in devices["IOS"]:
        MY_DEVICES.append( {
            "host": host,
            "transport": "asyncssh",
            "auth_username": username,
            "auth_password": password,
            "auth_strict_key": False,
            #"platform": "cisco_iosxe",
            "transport_options": {
                "asyncssh": {
                    "encryption_algs": ["aes128-cbc", "aes192-cbc", "aes256-ctr", "aes192-ctr"]
                }
            }
        } )
    
    # Async run em all
    coroutines = [async_scrapli_stuff(device) for device in MY_DEVICES]
    results = await asyncio.gather(*coroutines)
    
    for result in results:
        print(result[1].result)    #aka sh version


if __name__ == "__main__":
    argrequired = '--xml' not in sys.argv and '-x' not in sys.argv
    parser = argparse.ArgumentParser(description="Please use this syntax:")
    parser.add_argument("-k", "--key", help="Meraki API Key", type=str)
    parser.add_argument("-u", "--username", help="Username for Cisco Devices", type=str)
    parser.add_argument("-p", "--password", help="Password for Cisco Devices", type=str)
    parser.add_argument("-f", "--filename", help="Device List File (YAML)", type=str)
    parser.add_argument("-o", "--organization", help="Temp--Organization ID", type=str)
    parser.add_argument("-s", "--serial", help="Temp--S/N", type=str)
    args = parser.parse_args()

    api_key = args.key
    username = args.username
    password = args.password
    filename = args.filename

    if not api_key:
        api_key = input("Meraki API Key: ")
    if not username:
        username = input("Username for Cisco Devices: ")
    if not password:
        password = getpass("Password for Cisco Devices: ")
    if not filename:
        filename = input("Device List File: ")


    # Run program
    #cisco_stuff(username, password, filename)
    asyncio.get_event_loop().run_until_complete(async_cisco_stuff(username, password, filename))
    #meraki_stuff(api_key, args.organization, args.serial)

    # Done!
    print("\n\nComplete!\n")