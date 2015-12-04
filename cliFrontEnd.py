# Written by Jeffrey Liu and Kevin Echols as a CLI Front End for SIGMAnet
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


print "\n" * 40


print "==============================================================="
print "Thank you for using the configurator."
print "CLI Menu Written by Jeffrey Liu, Kevin Echols"
print "===============================================================\n"





def print_log():
	log = get_log()
	for line in log:
		print line

		
		
switches = switchconfig.get_switches()
switch_dict = {}

def write_switch_dict():
	iterations = 0
	for switch in switches['switches']:
		iterations += 1
		switch_dict[str(iterations)] = switch['ip_addr']


write_switch_dict()



def print_switches():
	iterations = 0
	for switch in switches['switches']:
		iterations += 1
		print str(iterations) + '.)  ' + switch['hostname'] + '     IP: ' + switch['ip_addr'] + '     Model: ' + switch ['model']


def selected_switch_name(switch_num):
	for switch in switches['switches']:
		if switch['ip_addr'] == switch_dict[switch_num]:
			return switch['hostname']


	
def config_switch():
	print '\nHere is a list of switches\n'
	print_switches()
	print "\nPlease enter switch a number.\n"
	switch_num = raw_input(">>>>>>>>>>>")
	
	switch_name = selected_switch_name(switch_num)

	selected_switch_ip = switch_dict[switch_num]

	print "\n\n\n\nLet me gather port and vlan information for switch: " + selected_switch_name(switch_num) + ".\n"

	print '\nGathering interface information...\n'
	intf = switchconfig.get_intfs(switch_dict[switch_num])
	print '\nGathering VLAN information...\n'
	vlan = switchconfig.get_vlans(switch_dict[switch_num])

	print 'Interfaces for %s:' % switch_dict[switch_num]
	for each in intf:
		print '\t' + each

	print '\nVLANs for %s:' % switch_dict[switch_num]
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

	conf_in = {"switch_ip": switch_dict[switch_num], "intf_desc": desc, "intf_id": intf_list, "vlan_id": vlan_input  }

	out = conf_intfs(conf_in)
	print "\n\nApplied configuration change:\n" + "=" * 40 + '\n' + out








def main():

	print 'Please choose what you would like to do:\n'
	
	print '1.)  Modify config on a switch'
	print '2.)  View the Audit Log'
	print '3.)  Exit\n'
	print "\nPlease enter a number.\n"
	option = raw_input(">>>>>>>>>>>")
	if option == '1':
		config_switch()
	elif option == '2':
		print_log()
	elif option == '3':
		exit()
	else:
		print '\nBad input, try again\n\n\n\n'

while True:
	main()