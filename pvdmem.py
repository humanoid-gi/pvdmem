# Main functions for parsing packet-via-dmem output on Juniper from Juniper MX

import re
import string
import subprocess
from datetime import datetime, timezone

CLEAR_FILES = True  # Delete temporary files after creating pcap

fake_eth_header = "0000face00000000face0000"


parcel_regexp = r'\n ([0-9a-f]{2,})'
packet_id_regexp = r'^(0x[0-9a-f]{8})'
packet_direction_regexp = r'\n(Dispatch|Reorder)'  # Dispatch: to LU / Reorder: from LU
pfenum_regexp = r'PfeNum (\d+)'
ptype_regexp = r'[\n ]PType (\S+)'
lu2lu_regexp = r'Lu2Lu_type (\S+)'
ddos_proto_regexp = r'DdosProto (\S+)'


def parse_raw_dump(dump):
    dump_list = []
    for packet in dump:
        # Find ID, direction and parcel in dump
        packet_id = re.search(packet_id_regexp, packet, re.DOTALL)
        packet_direction = re.search(packet_direction_regexp, packet, re.DOTALL)
        parcel = re.findall(parcel_regexp, packet, re.DOTALL)
        ptype = re.search(ptype_regexp, packet, re.DOTALL)
        lu2lu = re.search(lu2lu_regexp, packet, re.DOTALL)
        ddosp = re.search(ddos_proto_regexp, packet, re.DOTALL)

        # Special marker for parcels with "Lu2Lu_type LU_STEERING"
        lu2lu_str = ''
        if lu2lu:
            lu2lu_str = lu2lu.group(1)
        
        
        if packet_id and packet_direction and parcel:
            dump_list.append({"id": packet_id.group(1),
                              "direction": packet_direction.group(1).replace("Dispatch", "toLU")
                                                                    .replace("Reorder", "fromLU"),
                              "parcel": "".join(parcel),
                              "ptype": ptype,
                              "lu2lu": lu2lu_str,
                              "ddosp": ddosp
                              })
    
    return dump_list


# toTU - parse MQ/XQ->LU packets 
# fromLU - parse LU->MQ/XQ tackets
def make_clear_parsels(dump, clearify=True, toLU=True, fromLU=True):

    cleared_list = []
    for packet in dump:
        
        cleared_parcel = packet['parcel']

        if clearify:

            # Add fake Ethernet header if needed to packet from CP
            if packet['ptype']:
                if packet['ptype'].group(1) == 'MPLS':
                    cleared_parcel = fake_eth_header + '8847' + packet['parcel']
                
                elif packet['ptype'].group(1) == 'IPV4' and packet['ddosp']:
                    cleared_parcel = packet['parcel']
             
                elif packet['ptype'].group(1) == 'IPV4' and packet['lu2lu'] ==  'LU_STEERING':
                    cleared_parcel = packet['parcel'][2::]
                
                elif packet['ptype'].group(1) == 'IPV4':
                    cleared_parcel = fake_eth_header + '0800' + packet['parcel']
                
                elif packet['ptype'].group(1) == 'IPV6':
                    cleared_parcel = fake_eth_header + '86dd' + packet['parcel']
                                   
                else:
                    cleared_parcel =  packet['parcel']


        if ( packet['direction'] == 'toLU' and toLU ) or \
           ( packet['direction'] == 'fromLU' and fromLU):
            
            # Check if parcel without "drop" action. Appnd only non-drop.
            if len(cleared_parcel) > 2:
                cleared_list.append(cleared_parcel) 

    return cleared_list

# Create pcap file from 'dump_list' using test2pcap utility
def create_pcap(dump_list, txt_file, pcap_file):

    with open(txt_file, 'w') as ft:
        ft.write("\n".join(dump_list) + "\n")
    
    pcap_result = subprocess.run(["text2pcap", "-r", "^(?<data>[0-9a-fA-F]+)$", txt_file, pcap_file], capture_output=True, text=True)

    if CLEAR_FILES:
        clear_result = subprocess.run(["rm", txt_file])

    return pcap_result.stderr


