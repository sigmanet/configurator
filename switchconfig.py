#!/usr/bin/env python
# __author__ = 'TMagill'

from device import Device
import json
import xmltodict
import sys
import time
import datetime
def get_time():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st

def get_switches():
    '''
    This returns a dictionary of switch info to be presented to user.
    '''
    sw_dict = {"switches": [{"hostname": "N9K1", "ip_addr": "172.31.217.133", "model": "Nexus 9396"},
                            {"hostname": "N9K2", "ip_addr": "172.31.217.134", "model": "Nexus 9396"},
                            {"hostname": "N9K3", "ip_addr": "172.31.217.135", "model": "Nexus 9396"},
                            {"hostname": "N9K4", "ip_addr": "172.31.217.136", "model": "Nexus 9396"}]}
    return sw_dict

def get_switchname(switch_ip):
    """
    This does a reverse lookup of name for switch with given IP

    params:
    switch_ip (string): ip address of switch
    """
    sw_dict = get_switches()
    for switch in sw_dict['switches']:
        if switch['ip_addr'] == switch_ip:
            switch_hostname = switch['hostname']
    return switch_hostname

def get_intfs(switch_ip):
    """
    This connects to the chosen switch and gets all of the ports. and vlans.
    This is filtered to access ports only.
    """
    switch_user = 'admin'
    switch_pw = 'cisco123'

    switch = Device(ip=switch_ip, username=switch_user, password=switch_pw)
    switch.open()
    command = switch.show('show interface')
    show_dict = xmltodict.parse(command[1])
    results = show_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']
    intf_list = []
    for result in results:
        if 'eth_mode' in result and result['eth_mode'] == 'access':
            intf_list.append(result['interface'])
    return intf_list

def get_vlans(switch_ip):
    '''
    This connects to the chosen switch and gets all of the ports. and vlans.
    This is filtered to access ports only.
    '''
    switch_user = 'admin'
    switch_pw = 'cisco123'
    # Connect to switch
    switch = Device(ip=switch_ip, username=switch_user, password=switch_pw)
    switch.open()
    # Parse data into dictionary
    command = switch.show('show vlan')
    show_dict = xmltodict.parse(command[1])
    results = show_dict['ins_api']['outputs']['output']['body']['TABLE_vlanbrief']['ROW_vlanbrief']
    vlan_list = []
    for result in results:
        if 'USER' in  result['vlanshowbr-vlanname']:
            vlan_list.append([result['vlanshowbr-vlanid-utf'], result['vlanshowbr-vlanname']])
    # print json.dumps(show_dict, indent=4)
    return vlan_list

def show_run(switch_ip, intf_id):
    '''
    This accepts the switch info and and interface.

    params:
    switch_ip (string): ip address of switch
    intf_id (string): interface to check config
    '''

    switch_user = 'admin'
    switch_pw = 'cisco123'
    # Connect to switch
    switch = Device(ip=switch_ip, username=switch_user, password=switch_pw)
    switch.open()
    # Parse VLAN data into dictionary
    command = switch.show('show interface ' + intf_id + ' switchport')
    show_dict = xmltodict.parse(command[1])
    results = show_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']
    oper_mode = results['oper_mode']
    access_vlan = results['access_vlan']
    # Parse description data into dictionary
    command = switch.show('show interface ' + intf_id)
    show_dict = xmltodict.parse(command[1])
    results = show_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']
    if 'desc' in results:
        desc = 'description ' + results['desc']
    else:
        desc = "no description"
    # Create NXOS formatted text to return
    config_text = 'interface ' + intf_id + '\n  ' + desc + '\n  switchport mode ' + oper_mode + '\n  switchport access vlan ' + access_vlan + '\n!\n'
    return config_text

def log_change(log_str):
    '''
    This writes an entry to a log file

    params:
    log_str (string): Text to be written
    '''
    logname = "api_change_log.txt"
    logfile = open(logname, 'a')
    logfile.write(log_str)
    logfile.close()

def get_log():
    '''
    Opens logfile and returns results
    '''
    log_list = []
    logname = "api_change_log.txt"
    logfile = open(logname, 'r').read()
    for line in logfile.split('\n'):
        log_list.append(line)
    return log_list


def conf_intfs(conf_dict):
    '''
    This connects to the chosen switch and gets all of the ports. and vlans.
    This is filtered to access ports only.

    params:
    conf_dict (dictionary), example:

    {
    "switch_ip": "172.31.217.135",
    "intf_desc": "Configured by NXAPI",
    "intf_id": [
	"Ethernet1/1",
	"Ethernet1/2"
    ],
    "vlan_id": "31"
	}

    '''
    config_changes_list = ""
    switch_user = 'admin'
    switch_pw = 'cisco123'
    switch_ip = conf_dict['switch_ip']
    switch_name = get_switchname(switch_ip)
    # Connect to switch
    switch = Device(ip=switch_ip, username=switch_user, password=switch_pw)
    switch.open()
    # Parse data in to commands
    for item in range(len(conf_dict['intf_id'])):
        change_vlan = 'config t ; interface ' + conf_dict['intf_id'][item] + ' ; switchport access vlan ' + conf_dict['vlan_id']
        change_desc = 'config t ; interface ' + conf_dict['intf_id'][item] + ' ; description ' + conf_dict['intf_desc']
        # Send switch commands to NXAPI
        switch.conf(change_vlan)
        switch.conf(change_desc)
        # Generate NXOS-friendly config to return to consumer
        config_changes_list += show_run(switch_ip, conf_dict['intf_id'][item])
        # Log cli_conf call to local file
        logtime = get_time()
        log_change(logtime + ': ' + switch_name + '(' + switch_user + '): ' + change_vlan + '\n')
        log_change(logtime + ': ' + switch_name + '(' + switch_user + '): ' + change_desc + '\n')
    return config_changes_list

def main():

    switch_dict = get_switches()

    intfs = get_intfs('172.31.217.135')

    vlans = get_vlans('172.31.217.135')

    conf_in = {"switch_ip": "172.31.217.135", "intf_desc": "Configured by NX-API", "intf_id": ["Ethernet1/3", "Ethernet1/4"],"vlan_id": "31"}
    output = conf_intfs(conf_in)
    print output

if __name__ == "__main__":
    main()
