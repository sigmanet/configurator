# Written by Jeffrey Liu and Kevin Echols as a CLI Front End for SIGMAnet's
# configurator.
# Suggested Improvements:
# 	* Allow user to choose switch by model, hostname or ip_addr
# 	* Allow users to choose switchports to be configured by number
# 	* Check all user input to be sure it's in the correct format
#	* Clean up the format of output being printed to CLI
#
   

import switchconfig
from switchconfig import *
import json

print "Thank you for using the configurator."
print "Allow one moment while I gather the switch availability.\n"
switches = switchconfig.get_switches()
print json.dumps(switches, indent = 4)
print "\nWhat switch would you like to configure by hostname?"
switch = raw_input(">")
print "\nLet me gather port and vlan information for switch: " + switch + ".\n"

ip_addr = ''

for each in switches['switches']:
	if each['hostname'] == switch:
		ip_addr = each['ip_addr']

intf = switchconfig.get_intfs(ip_addr)
vlan = switchconfig.get_vlans(ip_addr)

print 'Interfaces for %s:' % ip_addr
for each in intf:
	print '\t' + each

print '\nVLANs for %s:' % ip_addr
for each in vlan:
	print 'VLAN ID: ' + each[0] + '\tVLAN Name: ' + each[1]
	print '=' * 40

print '\nHow many interfaces from the list would you like to configure?'
intf_range = input('>')

intf_list = []

for i in range(1, intf_range + 1):
	print 'What interface from the list would you like to configure? One per line.'
	intf_list.append(raw_input('%r.' % i))

print 'Which VLAN ID from the list would you like to add the selected port(s)?'
vlan_input = raw_input('>')

print 'What descritpion would you like to add?'
desc = raw_input('>')

conf_in = {"switch_ip": ip_addr, "intf_desc": desc, "intf_id": intf_list, "vlan_id": vlan_input  }

out = conf_intfs(conf_in)
print "\n\nApplied configuration change:\n" + "=" * 40 + '\n' + out
