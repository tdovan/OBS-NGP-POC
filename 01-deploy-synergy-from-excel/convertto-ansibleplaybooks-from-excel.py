###
# Copyright (2016-2019) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###
### -----------------------History
##    04-SEP : Works up to LIG with Ethernet-FC . TBD: FCOE
##    06-SEP :
##      - Scopes : ethernet-fc- lig - network set
##      - Enclosure group
##   08-SEP:
##      - Logical enclosure
##      - Update firmware
##      - Scopes to LE and EG
##   10-SEP: 
##      - server profiles
##   16-SEP:
##      - Add snmp and QOS to LIG
##   26-OCT:
##      - re-write generate_ansible_configuration to return prefix only ( with '-' at the end)
##      - write generate_oneview_config_coniguration to generate oneview_config.json im ymlfolder




from pprint import pprint
import json
import copy
import csv

import os
from os import sys

import shutil
from shutil import copy


from hpOneView.exceptions import HPOneViewException
from hpOneView.oneview_client import OneViewClient

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

TABSPACE        = "    "
COMMA           = ','
CR              = '\n'
CRLF            = '\r\n'
IC_OFFSET       = 3         # Used to calculate bay number from InterconnectBaySet
                            # InterconnectBaySet = 1 ---> Bay 1  and Bay 4
                            # InterconnectBaySet = 2 ---> Bay 1  and Bay 5
                            # InterconnectBaySet = 3 ---> Bay 1  and Bay 6


# Definition of resource types
resource_type_ov4_20    = {
    'subnet'                        : 'Subnet',
    'range'                         : 'Range',
    'timeandlocale'                 : 'TimeAndLocale',
    'scope'                         : 'ScopeV3',
# network
    'ethernet'                      : 'ethernet-networkV4',
    'fcnetwork'                     : 'fc-networkV4',
    'fcoenetwork'                   : 'fcoe-networkV4',
    'fc'                            : 'fc-networkV4',
    'fcoe'                         : 'fcoe-networkV4',
    'ethernetsettings'              : 'EthernetInterconnectSettingsV4',
    'networkset'                    : 'network-setV4',
    'logicalinterconnectgroup'      : 'logical-interconnect-groupV5',
    'snmp-configuration'            : 'snmp-configuration',
    'qos-aggregated-configuration'  : 'qos-aggregated-configuration',
    'qosconfiguration'              : 'QosConfiguration',
    'snmp-configuration'            : 'snmp-configuration',
    'enclosuregroup'                : 'EnclosureGroupV7',
# storage
    'storagevolumetemplate'         : 'StorageVolumeTemplateV6',
    'storagevolume'                 : 'StorageVolumeV7',
# server
    'logicalenclosure'              : 'LogicalEnclosureV4',
    'serverprofiletemplate'         : 'ServerProfileTemplateV5',
    'serverprofile'                 : 'ServerProfileV9',
    'clusterprofile'                : 'HypervisorClusterProfileV3'
}

resource_type_ov5_00    = {
    'subnet'                        : 'Subnet',
    'range'                         : 'Range',
    'timeandlocale'                 : 'TimeAndLocale',
    'scope'                         : 'ScopeV3',
# network
    'ethernet'                      : 'ethernet-networkV4',
    'fcnetwork'                     : 'fc-networkV4',
    'fcoenetwork'                   : 'fcoe-networkV4',    
    'fc'                            : 'fc-networkV4',
    'fcoe'                          : 'fcoe-networkV4',
    'ethernetsettings'              : 'EthernetInterconnectSettingsV6',
    'networkset'                    : 'network-setV5',
    'logicalinterconnectgroup'      : 'logical-interconnect-groupV7',
    'uplinkset'                     : 'uplinksetV6',
    'snmp-configuration'            : 'snmp-configuration',
    'qos-aggregated-configuration'  : 'qos-aggregated-configuration',
    'qosconfiguration'              : 'QosConfiguration',
    'snmp-configuration'            : 'snmp-configuration',
    'enclosuregroup'                : 'EnclosureGroupV7',
    
# storage
    'storagevolumetemplate'         : 'StorageVolumeTemplateV6',
    'storagevolume'                 : 'StorageVolumeV7',
# server
    'logicalenclosure'              : 'LogicalEnclosureV4',
    'serverprofiletemplate'         : 'ServerProfileTemplateV7',
    'serverprofile'                 : 'ServerProfileV11',
    'clusterprofile'                : 'HypervisorClusterProfileV3'
}

# Defintion of UplinkSet Ethernet Network type
uplinkSetEthernetNetworkType     = {
    'Ethernet'                      : 'Tagged',
    'Untagged'                      : 'Untagged',
    'Tunnel'                        : 'Tunnel',
    'ImageStreamer'                 : 'ImageStreamer'
}


# Definition of UplinkSet Network type
uplinkSetNetworkType        = {
    'Ethernet'                      : 'Ethernet',
    'FibreChannel'                  : 'FibreChannel',
    'Untagged'                      : 'Ethernet',
    'Tunnel'                        : 'Ethernet',
    'ImageStreamer'                 : 'Ethernet'
}

    # Definition of interconnect Type
interconnectNameType           = {
        'SEVC40F8'                      : 'Virtual Connect SE 40Gb F8 Module for Synergy',
        'SEVC100F32'                    : 'Virtual Connect SE 100Gb F32 Module for Synergy',
        'SE20ILM'                       : 'Synergy 20Gb Interconnect Link Module',
        'SE10ILM'                       : 'Synergy 10Gb Interconnect Link Module',
        'SE50ILM'                       : 'Synergy 50Gb Interconnect Link Module',
        'SEVC16GbFC'                    : 'Virtual Connect SE 16Gb FC Module for Synergy',
        'SEVC32GbFC'                    : 'Virtual Connect SE 32Gb FC Module for Synergy',
        'SEVCFC'                        : 'Virtual Connect SE 16Gb FC Module for Synergy',
        'SE12SAS'                       : 'Synergy12GbSASConnectionModule'

    }

    # Definition of driveTechnologyType
driveTechnologyType           = {
        'SAS'                           : 'SasHdd', 
        'SATA'                          : 'SataHdd',
        'SASSSD'                        : 'SasSsd',
        'SATASSD'                       : 'SataSsd',
        'NVMeSata'                      : 'NVMeHdd',
        'NVMeSAS'                       : 'NVMeSsd',
        'Unknown'                       : 'Unknown',
        'Auto'                          : 'Unknown'

    }



    # Definition of port speeds on uplinkset

setUplinkSetPortSpeeds = {
        '0'                              : "Speed0M",
        '100M'                           : "Speed100M",
        '100'                            : "Speed100M",
        '10G'                            : "Speed10G",
        '10'                             : "Speed10G",
        '10M'                            : "Speed10M",
        '1G'                             : "Speed1G",
        '1'                              : "Speed1G",
        '1M'                             : "Speed1M",
        '20G'                            : "Speed20G",
        '20'                             : "Speed20G",
        '25G'                            : "Speed25G",
        '25'                             : "Speed25G",
        '2G'                             : "Speed2G",
        '2'                              : "Speed2G",
        '2.5G'                           : "Speed2_5G",
        '40G'                            : "Speed40G",
        '50G'                            : "Speed50G",
        '50'                             : "Speed50G",
        '4G'                             : "Speed4G",
        '8G'                             : "Speed8G",
        '4'                              : "Speed4G",
        '8'                              : "Speed8G",
        '16'                             : "Speed16G",
        '32'                             : "Speed32G",
        'Auto'                           : "Auto"
}


# ================================================================================================
#
#   Build playbook headers
#
# ================================================================================================
def build_header(scriptCode):

    
    scriptCode.append("  hosts: localhost"                                                                                                          )       
    scriptCode.append("  vars:"                                                                                                                     )
    scriptCode.append("     config: \'oneview_config.json\'"                                                                                        )



# ================================================================================================
#
#   Write to file
#
# ================================================================================================
def write_to_file(scriptCode, filename):
    file                        = open(filename, "w")
    code                        = CR.join(scriptCode)
    file.write(code)

    file.close()



# ================================================================================================
#
#  find_port_number_in_interconnect_type
#
# ================================================================================================
def find_port_number_in_interconnect_type(allInterconnectTypes, icName,  portName):

    portNumber          = 0
    this_ic             = None

    if allInterconnectTypes:
        # find interconnect type by name
        for ic in allInterconnectTypes:
            if icName == ic['name']:
                this_ic = ic


        if this_ic:
            # find portInfos of this ic
            portInfos       = this_ic['portInfos']
            for p in portInfos:
                if portName == p['portName'] :
                    portNumber = p['portNumber']
    
    return portNumber

# ================================================================================================
#
#   HELPER: generate_id_pools_ipv4_subnets
#
# ================================================================================================

def generate_id_pools_ipv4_subnets(values_in_dict,scriptCode):  
    # ---- Note:
    #       This is to define only common code


    subnet                      = values_in_dict
    name                        = subnet['name']
    networkId                   = subnet['networkId']   
    subnetmask                  = subnet['subnetmask'] 
    gateway                     = subnet['gateway']
    domain                      = subnet['domain']

    scriptCode.append("                                                     "                                                                       )
    scriptCode.append("     - name: Create subnet                       "                                                                           )
    scriptCode.append("       oneview_id_pools_ipv4_subnet:             "                                                                           )
    scriptCode.append("         config:     \'{{config}}\'              "                                                                           )
    scriptCode.append("         state:      present                     "                                                                           )
    scriptCode.append("         data:                                   "                                                                           )
    scriptCode.append("             name:                            {} ".format(name)                                                              )
    scriptCode.append("             networkId:                       {} ".format(networkId)                                                         )
    scriptCode.append("             subnetmask:                      {} ".format(subnetmask)                                                        )
    scriptCode.append("             gateway:                         {} ".format(gateway)                                                           )
    scriptCode.append("             domain:                          {} ".format(domain)                                                            )
    scriptCode.append("             type:                            {} ".format(rstype['subnet'])                                                  )
    

    return scriptCode


# ================================================================================================
#
#   HELPER: generate_id_pools_ipv4_ranges
#
# ================================================================================================

def generate_id_pools_ipv4_ranges(values_in_dict,scriptCode):  
    # ---- Note:
    #       This is to define only common code

    pool                        = values_in_dict
    name                        = pool['name']
    startAddress                = pool['startAddress']
    endAddress                  = pool['endAddress']

    scriptCode.append(CR )
    scriptCode.append("     - name: Create Id pools                     "                                                                           )
    scriptCode.append("       oneview_id_pools_ipv4_range: "                                                                                        )
    scriptCode.append("         config:     \'{{config}}\'              "                                                                           )
    scriptCode.append("         state:      present                     "                                                                           )
    scriptCode.append("         data:                                   "                                                                           )
    scriptCode.append("             name:                         {}    ".format(name)                                                              )
    scriptCode.append("             enabled:                      True  "                                                                           )
    scriptCode.append("             type:                         {}    ".format(rstype['range'])                                                   )
    scriptCode.append("             startStopFragments:                 "                                                                           ) 
    
    if startAddress and endAddress:   
        sAddress        = startAddress.split('|')
        eAddress        = endAddress.split('|')
        for index, value in enumerate(sAddress):
            scriptCode.append("                - startAddress:           \'{}\' ".format(sAddress[index])                                            )
            scriptCode.append("                  endAddress:             \'{}\' ".format(eAddress[index])                                            )


    return scriptCode

# ================================================================================================
#
#   generate_id_pools_ipv4_ranges_subnets_ansible_script
#
# ================================================================================================
def generate_id_pools_ipv4_ranges_subnets_ansible_script(sheet, to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                         )
    scriptCode.append("- name:  Configure id pools ipv4 from csv"                                                                                   )    
    build_header(scriptCode)

    #####
    scriptCode.append("  tasks:"                                                                                                                    )
    
    if not sheet.empty:
        for i in sheet.index:
            row                         = sheet.loc[i]
            name                        = row['name']
            startAddress                = row['startAddress']
            endAddress                  = row['endAddress']
            poolType                    = row['poolType']
            if 'IPV4' in poolType:
                generate_id_pools_ipv4_subnets(row, scriptCode)

                dnsServers                      = str(row['dnsServers']) 
                if dnsServers:                                              # HKD6
                    dnsServers                  = dnsServers.split('|') 

                    scriptCode.append("             dnsServers:                         "                                                         )
                    for dns in dnsServers:
                        scriptCode.append("                 - {}                            ".format(dns)                                         )  
        
                scriptCode.append(CR)
                scriptCode.append("                                                     "                                                         )
                scriptCode.append("     - name: Get uri for subnet from {}          ".format(name)                                                )
                scriptCode.append("       oneview_id_pools_ipv4_subnet_facts: "                                                                   )
                scriptCode.append("         config:     \'{{config}}\'              "                                                             )
                scriptCode.append("         name:       \'{}\'                      ".format(name)                                                )
                scriptCode.append("     - set_fact:  " )
                var_name            = name.lower().replace('-','_').strip(' ')                         
                scriptCode.append("         subnet_{}_uri:".format(var_name) + " \'{{id_pools_ipv4_subnets[0].uri}}\'")

                generate_id_pools_ipv4_ranges(row,scriptCode)
                scriptCode.append("             subnetUri:                   \'{{" + "subnet_{}_uri".format(var_name)  + "}}\'"                   )



        # end of id pools
        scriptCode.append("       delegate_to: localhost                    "                                                                     )
        scriptCode.append(CR)


    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



# ================================================================================================
#
#   HELPER: generate_time_locale
#
# ================================================================================================

def generate_time_locale(values_in_dict,scriptCode):  
    # ---- Note:
    #       This is to define only common code


    time                        = values_in_dict
    locale                      = time['locale']
    timezone                    = time['timezone']   
    ntpServers                  = time['ntpServers'] # []

    scriptCode.append("                                                     "                                                                       )
    scriptCode.append("     - name: Create time and locale              "                                                                           )
    scriptCode.append("       oneview_appliance_time_and_locale_configuration: "                                                                    )
    scriptCode.append("         config: \'{{config}}\'                  "                                                                           )
    scriptCode.append("         state: present                          "                                                                           )
    scriptCode.append("         data:                                   "                                                                           )
    scriptCode.append("             locale:                          {} ".format(locale)                                                            )
    scriptCode.append("             timezone:                        {} ".format(timezone)                                                          )
    scriptCode.append("             type:                            {} ".format(rstype['timeandlocale'])                                           )
    





    

    return scriptCode

# ================================================================================================
#
#   generate_time_locale_ansible_script
#
# ================================================================================================
def generate_time_locale_ansible_script(sheet, to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                         )
    scriptCode.append("- name:  Configure time and locale         "                                                                                 )    
    build_header(scriptCode)

    scriptCode.append("  tasks:"                                                                                                                    )
    
    if not sheet.empty:
        for i in sheet.index:
            row                         = sheet.loc[i]
            generate_time_locale(row, scriptCode)
            ntpServers                  = row['ntpServers'] 
            ntpServers                  = str(ntpServers).split('|')
            if ntpServers:
                scriptCode.append("             ntpServers:                 "                                                                           )
                for ntp in ntpServers:
                    scriptCode.append("                 - {}                ".format(ntp)                                                               )  
        
        # end of time and locale
            scriptCode.append("       delegate_to: localhost                    "                                                                       )
            scriptCode.append(CR)


    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


# ================================================================================================
#
#   generate_scope_for_resource
#
# ================================================================================================
def generate_scope_for_resource(name, varNameUri, scope, scriptCode):

    list_of_scopes      = scope.split('|')
    for sc in list_of_scopes:
        scope_name      = sc
        scriptCode.append("                                                         "                                                   )
        scriptCode.append("     - name: Update the scope {0} with new resource {1}  ".format(scope_name,name)                           )
        scriptCode.append("       oneview_scope:                                    "                                                   )
        scriptCode.append("         config:       '{{ config }}'                    "                                                   )
        scriptCode.append("         state:        resource_assignments_updated      "                                                   )
        scriptCode.append("         data:                                           "                                                   )
        scriptCode.append("             name:     {}                                ".format(scope_name)                                )
        scriptCode.append("             resourceAssignments:                        "                                                   )
        scriptCode.append("                 addedResourceUris:                      "                                                   )
        scriptCode.append("                     - {}                                ".format(varNameUri)                                )    


# ================================================================================================
#
#    get_subnet_uri_from_id
#
# ================================================================================================
def get_subnet_uri_from_id(name, _type, scriptCode):

    fact              = 'oneview_{0}_facts'.format(_type)
    fact_result       = "\'{{" + "{}s".format(_type) + "}}\'"
    var               = 'var_' + name.lower().strip().replace(',', '_').replace('-', '_').replace(' ', '').replace('.', '_')
    

    scriptCode.append("                                                         "                                                       )
    scriptCode.append("     - name: get uri for subnet {}                       ".format(name)                                          )
    scriptCode.append("       {}:                                               ".format(fact)                                          )
    scriptCode.append("         config:        \'{{config}}\'                   "                                                       )
    scriptCode.append("     - set_fact:                                         "                                                       )
    scriptCode.append("          networkId:    \'{}\'                           ".format(name)                                          )  
    scriptCode.append("          var_subnets:  {}                               ".format(fact_result)                                   )
    scriptCode.append("     - set_fact:                                         "                                                       )
    scriptCode.append("          var_uri:    \'{{item.uri}}\'                   "                                                       )  
    scriptCode.append("       loop:  \'{{var_subnets}}\'                        "                                                       )  
    scriptCode.append("       when:  item.networkId == networkId                "                                                       ) 
    return "{{var_uri}}"

# ================================================================================================
#
#   generate_bandwidth_for_resource
#
# ================================================================================================
def generate_bandwidth_for_resource(name, _type, typicalBandwidth, maximumBandwidth, scriptCode):

        fact              = 'oneview_{0}_facts'.format(_type)

        # Query resource first
        var               = 'var_' + name.lower().strip().replace(',', '_').replace('-', '_').replace(' ', '')
        scriptCode.append("                                                         "                                                  )
        scriptCode.append("     - name: get resource {}                             ".format(name)                                     )
        scriptCode.append("       {}:                                               ".format(fact)                                     )
        scriptCode.append("         config:     \'{{config}}\'                      "                                                  )
        scriptCode.append("         name:       \'{}\'                              ".format(name)                                     )
        scriptCode.append("     - set_fact:                                         "                                                  )
        scriptCode.append("          {}: ".format(var)  + "\'{{" + "{0}s[0].connectionTemplateUri".format(_type) + "}}\' "             )
        uri               = "\'{{" + '{}'.format(var) + "}}\'"  



        scriptCode.append("                                                         "                                                   )
        scriptCode.append("     - name: Update bandwidth for resource {0}           ".format(name)                                      )
        scriptCode.append("       oneview_connection_template:                      "                                                   )
        scriptCode.append("         config:       '{{ config }}'                    "                                                   )
        scriptCode.append("         state:        present                           "                                                   )
        scriptCode.append("         data:                                           "                                                   )
        scriptCode.append("             uri:     {}                                 ".format(uri)                                       )
        scriptCode.append("             type:     'connection-template'             "                                                   )

        scriptCode.append("             bandwidth:                                  "                                                   )
        scriptCode.append("                 typicalBandwidth:       {}              ".format(typicalBandwidth)                          )
        scriptCode.append("                 maximumBandwidth:       {}              ".format(maximumBandwidth)                          )



# ================================================================================================
#
#   generate_firmware_bundle_ansible_script
#
# ================================================================================================
def generate_firmware_bundle_ansible_script(sheet, to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                          )
    scriptCode.append("- name:  Configure firmware bundle         "                                                                                  )    
    build_header(scriptCode)

    scriptCode.append("  tasks:"                                                                                                                     )
    
    for i in sheet.index:
        row                         = sheet.loc[i]
        name                        = row['name'] 
        filename                    = row['filename']

        scriptCode.append("                                                     "                                                                   )
        scriptCode.append("     - name: Upload firmware bundle   {}         ".format(name)                                                          )
        scriptCode.append("       oneview_firmware_bundle:                  "                                                                       )
        scriptCode.append("         config:         \'{{config}}\'          "                                                                       )
        scriptCode.append("         state: present                          "                                                                       )
        scriptCode.append("         file_path:      \'{}\'                  " .format(filename)                                                     ) 


    
    # end of firmware bundle
    scriptCode.append("       delegate_to: localhost                            "                                                                  )
    scriptCode.append(CR)

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



# ================================================================================================
#
#   generate_snmp_v1_ansible_script
#
# ================================================================================================
def generate_snmp_v1_ansible_script(sheet, to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                             )
    scriptCode.append("- name:  Configure snmp v1  from csv"                                                                                            )    
    build_header(scriptCode)

    scriptCode.append("  tasks:"                                                                                                                        )
    
    if not sheet.empty:
        for i in sheet.index:
            row             = sheet.loc[i]
            destination                 = row['destination'] 
            communityString             = row['communityString']
            port                        = row['port']

            scriptCode.append("                                                     "                                                                   )
            scriptCode.append("     - name: Create trap destination {}         ".format(destination)                                                    )
            scriptCode.append("       oneview_appliance_device_snmp_v1_trap_destinations:                  "                                            )
            scriptCode.append("         config:                 \'{{config}}\'  "                                                                       )
            scriptCode.append("         state: present                          "                                                                       )
            scriptCode.append("         data:                                   "                                                                       )
            scriptCode.append("             communityString:    \'{}\'          " .format(communityString)                                              )
            scriptCode.append("             destination:        \'{}\'          " .format(destination)                                                  )
            scriptCode.append("             port:               \'{}\'          " .format(port)                                                         )
        
        
                # end of snmp_v1
        scriptCode.append("       delegate_to: localhost                            "                                                                   )
        scriptCode.append(CR)

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



# ================================================================================================
#
#   generate_ansible_configuration
#
# ================================================================================================
def generate_ansible_configuration(versionSheet):
     


    # ============== Generate prefix =====================
    versionSheet.dropna(how='all', inplace=True)
    row = versionSheet.iloc[0]
    pod                 = row['Pod']
    site                = row['Site']
    if pod:
        pod             = pod.lower().strip()
    if site:
        site            = site.lower().replace(',', '-')
    
    prefix              = site + '-' + pod 


    return prefix

# ================================================================================================
#
#   generate_oneview_config_configuration
#
# ================================================================================================
def generate_oneview_config_configuration(composerSheet, to_file):
     
    print('Creating oneview config    =====>           {}'.format(to_file)) 

    # ================= generate oneview_config
    scriptCode = []
    composerSheet.dropna(how='all', inplace=True)
    row = composerSheet.iloc[0]
    name                     = row['name'].strip() 
    userName                 = row['userName'].strip()
    password                 = row['password'].strip()
    authDomain               = row['authenticationDomain'].strip()
    api_version              = row['api_version'].strip()
    scriptCode.append("{                                         "                                                                                  )
    scriptCode.append("     \"ip\":              \"{}\",         " .format(name)                                                                    )
    scriptCode.append("     \"credentials\" :    {               "                                                                                  )
    scriptCode.append("         \"userName\":    \"{}\",         " .format(userName)                                                                )
    scriptCode.append("         \"password\":    \"{}\"          " .format(password)                                                                )
    scriptCode.append("      },                                  "                                                                                  )
    scriptCode.append("     \"api_version\" :     \"{}\"         " .format(api_version)                                                             )
    scriptCode.append("}                                         "                                                                                  )

    scriptCode.append(CR)

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


# ================================================================================================
#
#   generate_scopes_ansible_script
#
# ================================================================================================

def generate_scopes_ansible_script(sheet, to_file):


    print('Creating ansible playbook   =====>           {}'.format(to_file))
    scriptCode = []
    scriptCode.append("---"                                                                                                                     )
    scriptCode.append("- name:  Configure scopes from csv"                                                                                      )    
    build_header(scriptCode)


    scriptCode.append("  tasks:"                                                                                                                )
    
    sheet                       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                     = sheet.loc[i]
            name                    = row["name"]                      
            description             = row["description"]                
            if name:
                scriptCode.append("                                                     "                                                               )
                scriptCode.append("     - name: Create scope  {}                    ".format(name)                                                      )
                scriptCode.append("       oneview_scope:                            "                                                                   )
                scriptCode.append("         config: \'{{config}}\'                  "                                                                   )
                scriptCode.append("         state: present                          "                                                                   )
                scriptCode.append("         data:                                   "                                                                   )
                scriptCode.append("             type:                       \'{}\'  ".format(rstype['scope'])                                           )
                scriptCode.append("             name:                       \'{}\'  ".format(name)                                                      )
                scriptCode.append("             description:                \'{}\'  ".format(description)                                               )
            
        

        # end of scopes
        scriptCode.append("       delegate_to: localhost                           "                                                                    )
        scriptCode.append(CR) 

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)

# ================================================================================================
#
#  generate_user_ansible_script
#
# ================================================================================================
def generate_user_ansible_script(sheet, to_file):

    print('Creating ansible playbook   =====>           {}'.format(to_file))
    scriptCode = []
    scriptCode.append("---"                                                                                                                     )
    scriptCode.append("- name:  Configure user         "                                                                                        )    
    build_header(scriptCode)

    columns_names                   = sheet.columns.tolist()
    sheet                           = sheet.sort_values(columns_names[0])
    sheet                           = sheet.applymap(str)                       # Convert data frame into string

    sheet                           = sheet[sheet[columns_names[0]]== 'OV']
    

    scriptCode.append("  tasks:"                                                                                                                )
    
    
    if not sheet.empty:
        for i in sheet.index:
            row                     = sheet.loc[i]
            name                    = row["name"]
            password                = row["password"]
            emailAddress            = row["emailAddress"]
            officePhone             = row["officePhone"]
            mobilePhone             = row["mobilePhone"]
            roles                   = row["roles"]
            scopePermissions        = row["scopePermissions"]

            name                    = name.strip()
            if name:
                if roles and scopePermissions:
                    list_roles      = roles.split('|')
                    list_perms      = scopePermissions.split('|')

                    for index,value in enumerate(list_perms): 
                        var_scope   = 'var_{}_uri'.format(value.strip().replace(' ', '').replace('-', '_').lower())

                        if value != 'all':                        
                            scriptCode.append(CR)
                            scriptCode.append("     - name: Get scope uri {}                            ".format(value)                                         )
                            scriptCode.append("       oneview_scope_facts:                              "                                                       )
                            scriptCode.append("         config: \'{{config}}\'                          "                                                       )
                            scriptCode.append("     - set_fact:                                         "                                                       )
                            scriptCode.append("          {}: ".format(var_scope) + "\'{{item.uri}}\'     "                                                       )  
                            scriptCode.append("       loop:  \'{{scopes}}\'                             "                                                       )  
                            scriptCode.append("       when:  item.name == \'{}\'                        ".format(value)                                         ) 
                          

                scriptCode.append(CR)
                scriptCode.append("     - name: Create user {}                      ".format(name)                                                      )
                scriptCode.append("       oneview_user:                             "                                                                   )
                scriptCode.append("         config: \'{{config}}\'                  "                                                                   )
                scriptCode.append("         state: present                          "                                                                   )
                scriptCode.append("         data:                                   "                                                                   )
                scriptCode.append("             name:                       \'{}\'  ".format(name)                                                      )
                scriptCode.append("             password:                   \'{}\'  ".format(password)                                                  )
                scriptCode.append("             emailAddress:               \'{}\'  ".format(emailAddress)                                              )
                scriptCode.append("             officePhone:                \'{}\'  ".format(officePhone)                                               )
                scriptCode.append("             mobilePhone:                \'{}\'  ".format(mobilePhone)                                               )
                scriptCode.append("             type:                       UserAndPermissions "                                                        )


                if roles:
                    scriptCode.append("             permissions:                    "                                                                   )
                    list_roles              = roles.split('|')
                    for index,value in enumerate(list_perms): 
                        scriptCode.append("                 - roleName:  {}         ".format(list_roles[index].strip().capitalize())                    )

                        value               = value.strip().replace(' ', '').replace('-', '_').lower()
                        if value != 'all': 
                            var_scope           = "\'{{var_" + "{}".format(value) + "_uri}}\'"
                            scriptCode.append("                   scopeUri:  {}         ".format(var_scope)                                             )
                        scriptCode.append(CR)

        # end of ethernet networks
        scriptCode.append("       delegate_to: localhost                            "                                                                   )
        scriptCode.append(CR) 

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



# ================================================================================================
#
#   generate_ethernet_networks_ansible_script
#
# ================================================================================================
def generate_ethernet_networks_ansible_script(sheet, to_file):

    print('Creating ansible playbook   =====>           {}'.format(to_file))
    scriptCode = []
    scriptCode.append("---"                                                                                                                     )
    scriptCode.append("- name:  Configure Ethernet networks         "                                                                           )    
    build_header(scriptCode)


    scriptCode.append("  tasks:"                                                                                                                )
    
    sheet                           = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                     = sheet.loc[i]
            name                    = row["name"]
            _type                   = row["type"].lower()
            vlanId                  = row["vlanId"]
            ethernetNetworkType     = row['ethernetNetworkType']
            subnetID                = row['subnetID']              
            ipV6subnetID            = row['ipV6subnetID']          
            typicalBandwidth        = int(1000 * float(row['typicalBandwidth']) )   if row['typicalBandwidth'] else 2500
            maximumBandwidth        = int(1000 * float(row['maximumBandwidth']))    if row['maximumBandwidth'] else 2500
            smartLink               = row["smartLink"].lower().capitalize()
            privateNetwork          = row["privateNetwork"].lower().capitalize()
            scope                   = row['scopes']                 
            purpose                 = row["purpose"]                                if  row["purpose"]             else 'General'
        
            varUri                  = ''
            if subnetID:
                varUri              =  get_subnet_uri_from_id(subnetID, 'id_pools_ipv4_subnet', scriptCode)

            scriptCode.append(CR)
            scriptCode.append("     - name: Create ethernet network {}          ".format(name)                                                      )
            scriptCode.append("       oneview_ethernet_network:                 "                                                                   )
            scriptCode.append("         config: \'{{config}}\'                  "                                                                   )
            scriptCode.append("         state: present                          "                                                                   )
            scriptCode.append("         data:                                   "                                                                   )
            scriptCode.append("             type:                       \'{}\'  ".format(rstype[_type])                                             )
            scriptCode.append("             name:                       \'{}\'  ".format(name)                                                      )
            scriptCode.append("             ethernetNetworkType:        {}      ".format(ethernetNetworkType)                                       )
            scriptCode.append("             purpose:                    {}      ".format(purpose)                                                   )
            scriptCode.append("             smartLink:                  {}      ".format(smartLink)                                                 )
            scriptCode.append("             privateNetwork:             {}      ".format(privateNetwork)                                            )
            scriptCode.append("             vlanId:                     {}      ".format(vlanId)                                                    )
            if varUri:
                scriptCode.append("             subnetUri:                  \'{}\'  ".format(varUri)                                                )
            scriptCode.append("             bandwidth:                          "                                                                   )
            scriptCode.append("                 typicalBandwidth:       {}      ".format(typicalBandwidth)                                          )
            scriptCode.append("                 maximumBandwidth:       {}      ".format(maximumBandwidth)                                          )
        
            # Add scope here
            
            if scope:
                netVar              = 'var_' + name.lower().strip().replace(',', '_').replace('-', '_').replace(' ', '') 
                scriptCode.append("                                                     "                                                           )
                scriptCode.append("     - name: get ethernet network {}             ".format(name)                                                  )
                scriptCode.append("       oneview_ethernet_network_facts:           "                                                               )
                scriptCode.append("         config:     \'{{config}}\'              "                                                               )
                scriptCode.append("         name:       \'{}\'                      ".format(name)                                                  )
                scriptCode.append("     - set_fact:                                 "                                                               )
                scriptCode.append("          {}: ".format(netVar)  + "\'{{ethernet_networks.uri}}\' "                                               )
                netUri              = "\'{{" + '{}'.format(netVar) + "}}\'"  
                generate_scope_for_resource(name, netUri, scope, scriptCode)
                



        # end of ethernet networks
        scriptCode.append("       delegate_to: localhost                    "                                                                       )
        scriptCode.append(CR) 

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)




# ================================================================================================
#
#   generate_network_sets_ansible_script
#
# ================================================================================================
def generate_network_sets_ansible_script(sheet, to_file):

    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                         )
    scriptCode.append("- name:  Configure network sets"                                                                                             )    
    build_header(scriptCode)


    scriptCode.append("  tasks:"                                                                                                                    )

    
    sheet                       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                     = sheet.loc[i]

            name                    = row['name']
            typicalBandwidth        = int(1000 * float(row['typicalBandwidth']))        if row['typicalBandwidth'] else 2500  
            maximumBandwidth        = int(1000 * float(row['maximumBandwidth']))        if row['maximumBandwidth'] else 2500
            networkSetType          = row['networkSetType']                             if  ["networkSetType"]         else 'Regular' 
            networks                = row["networks"]               
            scope                   = row['scopes']                 
        
            scriptCode.append("                                                 "                                                                    )
            scriptCode.append("     - name: Create network set {}               ".format(name)                                                       )
            scriptCode.append("       oneview_network_set:                      "                                                                    )
            scriptCode.append("         config: \'{{config}}\'                  "                                                                    )
            scriptCode.append("         state: present                          "                                                                    )
            scriptCode.append("         data:                                   "                                                                    )
            scriptCode.append("             type:                       \'{}\'  ".format(rstype['networkset'])                                       )
            scriptCode.append("             name:                       \'{}\'  ".format(name)                                                       )
            scriptCode.append("             networkSetType:             \'{}\'  ".format(networkSetType)                                             )


            if networks:
                networks = networks.split('|')

                if networks: 
                    scriptCode.append("             networkUris:                    "                                                                )
                    for net in networks:
                            scriptCode.append("                 - {}                ".format(net)                                                    )   

            _type = 'network_set'
            generate_bandwidth_for_resource(name, _type, typicalBandwidth, maximumBandwidth, scriptCode)
            # Add scope here
            
            if scope:
                netVar              = 'var_' + name.lower().strip().replace(',', '_').replace('-', '_').replace(' ', '')
                scriptCode.append("                                                     "                                                           )
                scriptCode.append("     - name: get network set {}             ".format(name)                                                       )
                scriptCode.append("       oneview_network_set_facts:           "                                                                    )
                scriptCode.append("         config:     \'{{config}}\'              "                                                               )
                scriptCode.append("         name:       \'{}\'                      ".format(name)                                                  )
                scriptCode.append("     - set_fact:                                 "                                                               )
                scriptCode.append("          {}: ".format(netVar)  + "\'{{network_sets[0].uri}}\' "                                                 )
                netUri              = "\'{{" + '{}'.format(netVar) + "}}\'"  
                generate_scope_for_resource(name, netUri, scope, scriptCode)

    




        scriptCode.append("       delegate_to: localhost                    "                                                                       )
        scriptCode.append(CR                                                                                                                        )







    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



# ================================================================================================
#
#   generate_fc_fcoe_networks_ansible_script
#
# ================================================================================================
def generate_fc_fcoe_networks_ansible_script(sheet, to_file):

    print('Creating ansible playbook   =====>           {}'.format(to_file))
    scriptCode = []
    scriptCode.append("---"                                                                                                                     )
    scriptCode.append("- name:  Configure fc/fcoe networks"                                                                                     )    
    build_header(scriptCode)


    scriptCode.append("  tasks:"                                                                                                                )
    sheet                       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                     = sheet.loc[i]
            name                    = row["name"]                           
            autoLoginRedistribution = row["autoLoginRedistribution"]        if  row["autoLoginRedistribution"]     else 'Auto'
            fabricType              = row["fabricType"]                     if  row["fabricType"]                  else 'FabricAttach'
            linkStabilityTime       = row["linkStabilityTime"]              if  row["linkStabilityTime"]           else 30        # default is 30 sec
            managedSanUri           = row["managedSan"]                     
            typicalBandwidth        = int(1000 * float(row['typicalBandwidth']))    if row['typicalBandwidth'] else 2500
            maximumBandwidth        = int(1000 * float(row['maximumBandwidth']))    if row['maximumBandwidth'] else 2500
            _type                   = row['type']
            vlanId                  = row['vlanId']
            scope                   = row['scopes']                                 
            _type                   = _type.lower()

            if name:
                if 'fc' == _type:
                    autoLoginRedistribution = autoLoginRedistribution.lower()
                    isAuto                  = 'auto' in autoLoginRedistribution

                    scriptCode.append("                                                 "                                                                   )
                    scriptCode.append("     - name: Create fc network {}                ".format(name)                                                      )
                    scriptCode.append("       oneview_fc_network:                       "                                                                   )
                    scriptCode.append("         config: \'{{config}}\'                  "                                                                   )
                    scriptCode.append("         state: present                          "                                                                   )
                    scriptCode.append("         data:                                   "                                                                   )
                    scriptCode.append("             type:                       \'{}\'  ".format(rstype['fc'])                                              )
                    scriptCode.append("             name:                       \'{}\'  ".format(name)                                                      )  
                    scriptCode.append("             autoLoginRedistribution:    {}      ".format(isAuto)                                                    )
                    scriptCode.append("             linkStabilityTime:          {}      ".format(linkStabilityTime)                                         )
                    scriptCode.append("             fabricType:                 {}      ".format(fabricType)                                                )
                    scriptCode.append("             managedSanUri:              \'{}\'  ".format(managedSanUri)                                             )


                    _type = 'fc_network'
                    generate_bandwidth_for_resource(name, _type, typicalBandwidth, maximumBandwidth, scriptCode)         

                else:
                    scriptCode.append("                                                 "                                                                   )
                    scriptCode.append("     - name: Create fcoe network {}              ".format(name)                                                      )
                    scriptCode.append("       oneview_fcoe_network:                     "                                                                   )
                    scriptCode.append("         config: \'{{config}}\'                  "                                                                   )
                    scriptCode.append("         state: present                          "                                                                   )
                    scriptCode.append("         data:                                   "                                                                   )
                    scriptCode.append("             type:                       \'{}\'  ".format(rstype['fcoe'])                                            )
                    scriptCode.append("             name:                       \'{}\'  ".format(name)                                                      )
                    scriptCode.append("             vlanId:                     {}      ".format(vlanId)                                                    )
                    scriptCode.append("             managedSanUri:              \'{}\'  ".format(managedSanUri)                                             )

  
                    _type = 'fcoe_network'
                    generate_bandwidth_for_resource(name, _type, typicalBandwidth, maximumBandwidth, scriptCode)          
                    

                # Add scope here
                
                if scope:
                    netVar              = 'var_' + name.lower().strip().replace(',', '_').replace('-', '_').replace(' ', '')
                    scriptCode.append("                                                             "                                                   )
                    scriptCode.append("     - name: get fc or fcoe network {}                       ".format(name)                                      )
                    if 'fc' == _type:
                        scriptCode.append("       oneview_fc_network_facts:                         "                                                   )
                    else:
                        scriptCode.append("       oneview_fcoe_network_facts:                       "                                                   )
                    scriptCode.append("         config:     \'{{config}}\'                          "                                                   )
                    scriptCode.append("         name:       \'{}\'                                  ".format(name)                                      )
                    scriptCode.append("     - set_fact:                                             "                                                   )
                    if 'fc' == _type:
                        scriptCode.append("          {}: ".format(netVar)  + "\'{{fc_networks[0].uri}}\' "                                              )
                    else:
                        scriptCode.append("          {}: ".format(netVar)  + "\'{{fcoe_networks[0].uri}}\' "                                            )
                    netUri              = "\'{{" + '{}'.format(netVar) + "}}\'"  
                    generate_scope_for_resource(name, netUri, scope, scriptCode)
                


        # end of fc networks
        scriptCode.append("       delegate_to: localhost                    "                                                                           )
        scriptCode.append(CR) 

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)




##

# ================================================================================================
#
#   HELPER: generate_logical_interconnect_groups
#
# ================================================================================================

def generate_logical_interconnect_groups(values_in_dict,snmpsheet,scriptCode, isFC=False, comeFromOV=False):  
    # ---- Note:
    #       This is to define only common code

    lig                         = values_in_dict
    name                        = lig["name"]                   
    enclosureType               = lig["enclosureType"]          if lig["enclosureType"]   else 'SY12000' 

    interconnectBaySet          = lig["interconnectBaySet"]
    redundancyType              = lig["redundancyType"]         if lig["redundancyType"]   else 'Redundant'


    if not isFC:
        # ethernetSettings

        ethernetSettings            = lig
        ethernetSettingsType        = rstype['ethernetsettings'] 

        igmpSnooping                = ethernetSettings["enableIgmpSnooping"].lower().capitalize()               if ethernetSettings["enableIgmpSnooping"]           else "False"
        igmpIdleTimeout             = ethernetSettings["igmpIdleTimeoutInterval"]                               if ethernetSettings["igmpIdleTimeoutInterval"]      else "260"
        networkLoopProtection       = ethernetSettings["enableNetworkLoopProtection"].lower().capitalize()      if ethernetSettings["enableNetworkLoopProtection"]  else "False"
        pauseFloodProtection        = ethernetSettings["enablePauseFloodProtection"].lower().capitalize()       if ethernetSettings["enablePauseFloodProtection"]   else "False"
        enableRichTLV               = ethernetSettings["enableRichTLV"].lower().capitalize()                    if ethernetSettings["enableRichTLV"]                else "False"
        taggedLldp                  = ethernetSettings["enableTaggedLldp"].lower().capitalize()                 if ethernetSettings["enableTaggedLldp"]             else "False"

        lldpIpAddressMode           = ethernetSettings["lldpIpAddressMode"]                                     if ethernetSettings["lldpIpAddressMode"]            else 'IPv4'
        lldpIpv6Address             = ethernetSettings["lldpIpv6Address"]                                       
        lldpIpv4Address             = ethernetSettings["lldpIpv4Address"]                                       

        fastMacCacheFailover        = ethernetSettings["enableFastMacCacheFailover"].lower().capitalize()       if ethernetSettings["enableFastMacCacheFailover"]   else "False"
        macRefreshInterval          = ethernetSettings["macRefreshInterval"]                                    if ethernetSettings["macRefreshInterval"]           else "30"

        #  storm Control
        enableStormControl          = ethernetSettings['enableStormControl'].lower().capitalize()               if ethernetSettings["enableStormControl"]           else "False"
        if 'True' in enableStormControl:
            stormControlPollingInterval = ethernetSettings['stormControlPollingInterval']                       if ethernetSettings["stormControlPollingInterval"]  else "1"
            stormControlThreshold       = ethernetSettings['stormControlThreshold']                             if ethernetSettings["stormControlThreshold"]        else "1"

        ## QOS configuration
        configType	                = lig['qosconfigType']                  if lig['qosconfigType']                else 'Passthrough'
        downlinkClassificationType	= lig['downlinkClassificationType']     if lig['downlinkClassificationType']   else 'DOT1P_AND_DSCP'
        uplinkClassificationType    = lig['uplinkClassificationType']       if lig['uplinkClassificationType']     else 'DOT1P'
        


       
            
    ## SNMP configuration - Apply to both VC-Ethernet and VC-FC
    ### HKD07 - TBD

    subsetsnmpsheet                     = pd.DataFrame()
    if not snmpsheet.empty:
        columns_names                   = snmpsheet.columns.tolist()
        snmpsheet                       = snmpsheet.sort_values(columns_names[0])
        snmpsheet                       = snmpsheet.applymap(str)                       # Convert data frame into string
        subsetsnmpsheet                 = snmpsheet[snmpsheet[columns_names[0]]== name]

        if  not subsetsnmpsheet.empty: 
            for i in subsetsnmpsheet.index:
                row                         = subsetsnmpsheet.loc[i]
                v1Enabled                   = 'true'                    if row['v1Enabled']            else 'false'
                readCommunity               = row['readCommunity']      if row['readCommunity']        else ''
                systemContact               = row['systemContact']      if row['systemContact']        else ''
                snmpUsers                   = row['snmpUsers']               #[]
                authPassword                = row['authPassword']            #[]
                privacyPassword             = row['privacyPassword']         #[]
                v3AuthProtocol              = row['v3AuthProtocol']          #[]
                v3PrivacyProtocol           = row['v3PrivacyProtocol']       #[]
                trapDestination             = row['trapDestination']         #[]
                trapPort                    = row['trapPort']                #[]
                trapFormat                  = row['trapFormat']              #[]
                notificationType            = row['notificationType']        #[]
                trapCommunityString         = row['trapCommunityString']     #[]
                engineId                    = row['engineId']                #[]
                users                       = row['users']                   #[]


                # work on snmp users
                list_snmpUsers              = snmpUsers.split('|')           if snmpUsers           else []
                list_authPassword           = authPassword.split('|')        if authPassword        else []
                list_privacyPassword        = privacyPassword.split('|')     if privacyPassword     else []
                list_v3AuthProtocol         = v3AuthProtocol.split('|')      if v3AuthProtocol      else []
                list_v3PrivacyProtocol      = v3PrivacyProtocol.split('|')   if v3PrivacyProtocol   else []


                # trap destination
                list_trapDestination        = trapDestination.split('|')     if trapDestination     else []
                list_trapPort               = trapPort.split('|')            if trapPort            else []
                list_trapFormat             = trapFormat.split('|')          if trapFormat          else []
                list_notificationType       = notificationType.split('|')    if notificationType    else []
                list_users                  = users.split('|')               if users               else []
                list_engineId               = engineId.split('|')            if engineId            else []
                list_trapCommunityString    = trapCommunityString.split('|') if trapCommunityString else []
                



    scriptCode.append("                                                     "                                                                       )
    scriptCode.append("     - name: Create logical interconnect group {}".format(name)                                                              )
    scriptCode.append("       oneview_logical_interconnect_group:       "                                                                           )
    scriptCode.append("         config: \'{{config}}\'                  "                                                                           )
    scriptCode.append("         state: present                          "                                                                           )
    scriptCode.append("         data:                                   "                                                                           )
    scriptCode.append("             name:                        \'{}\' ".format(name)                                                              )
    scriptCode.append("             type:                        \'{}\' ".format(rstype['logicalinterconnectgroup'])                                )
    scriptCode.append("             enclosureType:               {}     ".format(enclosureType)                                                     )
    scriptCode.append("             interconnectBaySet:          {}     ".format(interconnectBaySet)                                                )
    scriptCode.append("             redundancyType:              {}     ".format(redundancyType)                                                    )


    if not isFC:
        scriptCode.append(CR)
        scriptCode.append("             ethernetSettings:                           "                                                               )
        scriptCode.append("                 type:                           {}      ".format(rstype['ethernetsettings'])                            )
        scriptCode.append("                 enableIgmpSnooping:             {}      ".format(igmpSnooping)                                          )
        if 'True' in igmpSnooping:
            scriptCode.append("                 igmpIdleTimeoutInterval:        {}  ".format(igmpIdleTimeout)                                       )

        scriptCode.append("                 enableNetworkLoopProtection:    {}      ".format(networkLoopProtection)                                 )
        scriptCode.append("                 enablePauseFloodProtection:     {}      ".format(pauseFloodProtection)                                  )
        scriptCode.append("                 enableRichTLV:                  {}      ".format(enableRichTLV)                                         )

        scriptCode.append("                 enableFastMacCacheFailover:     {}      ".format(fastMacCacheFailover)                                  )
        if 'True' in fastMacCacheFailover:
            scriptCode.append("                 macRefreshInterval:             {}  ".format(macRefreshInterval)                                    )

        scriptCode.append("                 enableStormControl:             {}      ".format(enableStormControl)                                    )
        if 'True' in enableStormControl:
            scriptCode.append("                 stormControlPollingInterval:    {}  ".format(stormControlPollingInterval)                           )
            scriptCode.append("                 stormControlThreshold:          {}  ".format(stormControlThreshold)                                 )  

        scriptCode.append("                 enableTaggedLldp:               {}      ".format(taggedLldp)                                            )
        if 'True' in taggedLldp:
            scriptCode.append("                 lldpIpv4Address:                {}  ".format(lldpIpv4Address)                                       )
            scriptCode.append("                 lldpIpv6Address:                {}  ".format(lldpIpv6Address)                                       )

        #### NEED TO WORK on TRAFFIC CLASS IDENTIFIERS
        ### QOS configuration
        #scriptCode.append(CR)
        #scriptCode.append("             qosConfiguration:                           "                                                               )
        #scriptCode.append("                 type:                               {}  ".format(rstype['qos-aggregated-configuration'])                )
        #scriptCode.append("                 activeQosConfig:                        "                                                               )
        #scriptCode.append("                     type:                           {}  ".format(rstype['qosconfiguration'])                            )
        #scriptCode.append("                     configType:                     {}  ".format(configType)                                            )
         
        #if 'custom' in configType.lower():
        #    scriptCode.append("                     uplinkClassificationType:       {}  ".format(uplinkClassificationType)                          )              
        #    scriptCode.append("                     downlinkClassificationType:     {}  ".format(downlinkClassificationType)                        )            

    ## SNMP configuration - Apply to both VC-Ethernet and VC-FC
    if not subsetsnmpsheet.empty: 
        scriptCode.append(CR)
        scriptCode.append("             snmpConfiguration:                          "                                                                   )
        scriptCode.append("                 type:                           {}      ".format(rstype['snmp-configuration'])                              )
        scriptCode.append("                 enabled:                        {}      ".format(v1Enabled)                                                 )
        scriptCode.append("                 v3Enabled:                      True    "                                                                   )
        scriptCode.append("                 readCommunity:                  {}      ".format(readCommunity)                                             )
        scriptCode.append("                 systemContact:                  {}      ".format(systemContact)                                             )
        if list_snmpUsers:
            scriptCode.append("                 snmpUsers:                              "                                                               )
            for i in range(len(list_snmpUsers)):
                scriptCode.append("                     - snmpV3UserName:           {}  ".format(list_snmpUsers[i])                                     )
                if 'NA' not in list_v3AuthProtocol[i].upper():
                    scriptCode.append("                       v3AuthProtocol:           {}  ".format(list_v3AuthProtocol[i])                            )
                    scriptCode.append("                       userCredentials:              "                                                           )
                    scriptCode.append("                         - propertyName:         SnmpV3AuthorizationPassword "                                   )
                    scriptCode.append("                           value:                {} ".format(list_authPassword[i])                               )
                    scriptCode.append("                           valueFormat:          SecuritySensitive "                                             )
                    if 'NA' not in list_v3PrivacyProtocol[i].upper():
                        scriptCode.append("                         - propertyName:         SnmpV3PrivacyPassword "                                     )
                        scriptCode.append("                           value:                {} ".format(list_privacyPassword[i])                        )
                        scriptCode.append("                           valueFormat:          SecuritySensitive "                                         )                        

                        scriptCode.append("                       v3PrivacyProtocol:        {}  ".format(list_v3PrivacyProtocol[i])                     )

        if list_trapDestination:
            scriptCode.append("                 trapDestinations:                       "                                                               )
            for i in range(len(list_trapDestination)):
                scriptCode.append("                     - trapDestination:           {} ".format(list_trapDestination[i])                               )
                scriptCode.append("                       port:                      {} ".format(list_trapPort[i])                                      )
                scriptCode.append("                       trapFormat:                {} ".format(list_trapFormat[i])                                    )
                scriptCode.append("                       userName:                  {} ".format(list_users[i])                                         )
                if 'v3' in list_trapFormat[i].lower()  and 'inform' in list_notificationType[i] :
                    scriptCode.append("                       inform:                    True "                                                         )
                    scriptCode.append("                       engineId:                  {} ".format(list_engineId[i])                                  )                   
                if 'v1' in list_trapFormat[i].lower() : 
                    scriptCode.append("                       communityString:           {} ".format(list_trapCommunityString[i])                       )   

    return scriptCode



# ================================================================================================
#
#   HELPER: generate_sas_logical_interconnect_groups
#
# ================================================================================================

def generate_sas_logical_interconnect_groups(values_in_dict,scriptCode):  
    # ---- Note:
    #       This is to define only common code

    lig                         = values_in_dict
    name                        = lig["name"]                                   
    enclosureType               = lig["enclosureType"]                          if  lig["enclosureType"]           else 'SY12000' 
    interconnectBaySet          = lig["interconnectBaySet"]
    

    scriptCode.append(CR)
    scriptCode.append("     - name: Create SAS logical interconnect group {}".format(name)                                                          )
    scriptCode.append("       oneview_sas_logical_interconnect_group:       "                                                                       )
    scriptCode.append("         config:                          \'{{config}}\'"                                                                    )
    scriptCode.append("         state:                           present"                                                                           )
    scriptCode.append("         data:                                   "                                                                           )
    scriptCode.append("             name:                        \'{}\' ".format(name)                                                              )
    scriptCode.append("             enclosureType:               {}     ".format(enclosureType)                                                     )
    scriptCode.append("             interconnectBaySet:          {}     ".format(interconnectBaySet)                                                )



    

    return scriptCode


def build_logicalPortConfig_Array(upl_logicalPortConfigs,isFC, fabricModuleType):


    arr_logicalPortConfigs                  = []
    upl_logicalPortConfigs                  = upl_logicalPortConfigs.replace(CRLF, '|').replace(CR,'|')
    arr_configs                             = upl_logicalPortConfigs.split('|')

    icName                                  = interconnectNameType[fabricModuleType]                        # 'SEVC40F8'                      : 'Virtual Connect SE 40Gb F8 Module for Synergy',
    
    for config in arr_configs:                               # format expected is--->  Enclosure1:Bay3:Q1|Enclosure1:Bay6:Q1
        if ':' in config:
            if isFC: 
                bay,portName            =  config.split(':')                                            #No enclousre for FC
                enclosureIndex          = -1
                portName                = portName.replace('Q', '')                                         # for FC, remove Q in front
                ic_location             = bay

            else:
                enclosure,bay,portName  = config.split(':')
                ic_location             = enclosure + ':' + bay                 # re-build enclosure1:Bay3
                portName                = portName.replace('.' , ':')           # port in Interconnect type sis defined as Q4:1
                enclosure               = enclosure.lower().strip()
                enclosure               = enclosure.replace('frame', 'enclosure') # standardize on enclosure1
                enclosureIndex          = enclosure.replace('enclosure', '')    # get Index

            
            ic_location             = ic_location.lower().replace(':', '_') # recycle ic_location to be used in var

            # We have interconnect name and portName. Now go find port Number from interconnect type
            # Note: ov_interconnect_types come from the query to OV                    

            portNumber              = find_port_number_in_interconnect_type(ov_interconnect_types, icName, portName )

            element = {
                "enclosureIndex"    : enclosureIndex,
                "bay"               : bay,
                "ic_location"       : ic_location,
                "portName"          : portName,
                "portNumber"        : portNumber
            } 

            arr_logicalPortConfigs.append(element)

    return arr_logicalPortConfigs

####
# ================================================================================================
#
#   generate_logical_interconnect_groups_ansible_script
#
# ================================================================================================
def generate_logical_interconnect_groups_ansible_script(sheet, uplsheet, snmpsheet, to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))
    scriptCode = []
    scriptCode.append("---"                                                                                                                     )
    scriptCode.append("- name:  Configure logical_interconnect_groups"                                                                          )    
    build_header(scriptCode)

    # Dictionary to find the Interconnect name per bay
    # This will be used by uplinkset to find port number for each uplink from VC to production network and FC ( Q1, Q2....)
    ICTYPE_BAY                  = dict()


    ## Configure logical interconnect group
    scriptCode.append("  tasks:"                                                                                                                    )

    sheet       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                         = sheet.loc[i]
            name                        = row["name"]                           
            bayConfig                   = row["bayConfig"]                      
            fabricModuleType            = row["fabricModuleType"]       
       
            if 'FC' in fabricModuleType:
                isFC                    = True
            else:
                isFC                    = False
            if 'SAS' in bayConfig:
                isSAS                   = True
            else:
                isSAS                   = False

            if isSAS:
                generate_sas_logical_interconnect_groups(row,scriptCode) # get common code first
            else:
                generate_logical_interconnect_groups(row,snmpsheet, scriptCode, isFC,comeFromOV=False) # get common code first

            # Scope
            scope                       = row['scopes']                       


            # Number of frames
            frameCount                  = row["frameCount"]                 if  row["frameCount"]              else 0       
            frameCount                  = int(frameCount)
            scriptCode.append(CR)
            scriptCode.append("             enclosureIndexes:                   "                                                                       )
        
            for index in range(1, frameCount+1):
                if 'FC' in fabricModuleType:
                    index               = -1
                scriptCode.append("                 - {}                        ".format(index)                                                         )


            # Map entry template
            if bayConfig:
                    scriptCode.append("             interconnectMapTemplate:            "                                                               )
                    scriptCode.append("                 interconnectMapEntryTemplates:  "                                                               )
                    
                    bay_config_list         = bayConfig.split(CR)
                    #bay_config_list         = bayConfig.split(CRLF)
                    for bay_config in bay_config_list:
                        if '{' in bay_config:

                            frame, config       = bay_config.split('{')
                            config              = config.rstrip(' ').rstrip('}')                                # remove ' }'
                            frame               = frame.replace(' ' , '').replace('=' , '')                     # remove ' = '
                            frame_name          = frame.lower().strip() + '_'                                   # Format  is enclosure1_ --> will be used in ICTYPE_BAY dict
                            frame_name          = frame_name.replace('frame', 'enclosure')                      # stanadrzie on naming frame : enclosure1_

                            enclosureIndex      = frame_name.lower().replace('enclosure','').replace('_', '')
                            bay_lists           = config.split('|')
                            for el in bay_lists:
                                bay, icType     = el.split('=')                                
                                bay_number      = bay.lower().strip()                                           # format is bay3 --> will be used in ICTYPE_BAY dict

                                icType          = icType.replace("'", "")
                                icType          = interconnectNameType[icType]
                                
                                
                                
                                if 'FC' in icType:
                                    enclosureIndex  = -1
                                bay             = bay.lower().replace('bay','')
                                if isSAS:
                                    icType      = icType.replace(' ' , '')
                                    icType      = '/rest/sas-interconnect-types/' + icType
                                    scriptCode.append("                     - permittedInterconnectTypeUri:     {}     ".format(icType)                     )
                                else:
                                    scriptCode.append("                     - permittedInterconnectTypeName:    {}     ".format(icType)                     )
                                scriptCode.append("                       enclosureIndex:                   {}         ".format(enclosureIndex)             )
                                scriptCode.append("                       logicalLocation:                             "                                    )
                                scriptCode.append("                         locationEntries:                           "                                    )
                                scriptCode.append("                             - type:                     \'{}\'     ".format('Bay')                      )
                                scriptCode.append("                               relativeValue:            {}         ".format(bay)                        )
                                scriptCode.append("                             - type:                     \'{}\'     ".format('Enclosure')                )                                
                                scriptCode.append("                               relativeValue:            {}         ".format(enclosureIndex)             )


                    

            # Add scope here
            if not isSAS:        
                if scope:
                    netVar              = 'var_' + name.lower().strip().replace(',', '_').replace('-', '_').replace(' ', '')
                    scriptCode.append("                                                             "                                                   )
                    scriptCode.append("     - name: get LIG                {}                       ".format(name)                                      )
                    scriptCode.append("       oneview_logical_interconnect_group_facts:             "                                                   )
                    scriptCode.append("         config:     \'{{config}}\'                          "                                                   )
                    scriptCode.append("         name:       \'{}\'                                  ".format(name)                                      )
                    scriptCode.append("     - set_fact:                                             "                                                   )
                    scriptCode.append("          {}: ".format(netVar)  + "\'{{logical_interconnect_groups[0].uri}}\' "                                  )

                    netUri              = "\'{{" + '{}'.format(netVar) + "}}\'"  
                    generate_scope_for_resource(name, netUri, scope, scriptCode)


                
        ## -------------------------------------------------
        ## Configure uplink set per LIG

        
        # Sort based on LIG name 
        
        columns_names               = uplsheet.columns.tolist()
        uplsheet                    = uplsheet.sort_values(columns_names[0])
        uplsheet.dropna(how='all', inplace=True)
        uplsheet                    = uplsheet.applymap(str)                       # Convert data frame into string

        # 1 - open uplinkset sheet to get facts and set vars 
        if not uplsheet.empty:
            for i in uplsheet.index:
                row                     = uplsheet.loc[i]

                fabricModuleType        = row["fabricModuleType"]
                nativeNetworkUri        = row["nativeNetwork"]              
                networkUris             = row["networks"]                       # Ex: rhosp3_storage|Vlan3100-1|Vlan_501|rhosp3_storage_mgmt
                networkSetUris          = row["networkSets"]                    # Ex: ns1|ns2
                upl_logicalPortConfigs  = row["logicalPortConfigInfos"]        #[]
                networkType             = row['networkType']


                networkType             = uplinkSetNetworkType[networkType]
                isFC                    = 'FibreChannel' == networkType
                isEthernet              = not isFC

                ## Define var for networks and networkSets first 

                if networkSetUris:
                    networkSetUris          = networkSetUris.split('|') 
                    for netset in networkSetUris:
                        netsetName          = netset.strip(' ')
                        netsetName          = netsetName.lower().strip().replace('-', '_')
                        netsetVar           = 'var_' + netsetName.replace(' ', '_')
            
                        scriptCode.append("                                                 "                                                                           )
                        scriptCode.append("     - name: Get uri for network Set {0}         ".format(netsetName)                                                        )
                        scriptCode.append("       oneview_network_set_facts:           "                                                                                )
                        scriptCode.append("         config: \'{{config}}\'                  "                                                                           )
                        scriptCode.append("         name:   \'{}\'                          ".format(netsetName)                                                        )    
                        scriptCode.append("     - set_fact:                                 "                                                                           )
                        scriptCode.append("          {}: ".format(netsetVar)  + "\'{{network_sets[0].uri}}\' "                                                          )  
                        scriptCode.append(CR)

                if networkUris:
                    networkUris             = networkUris.split('|')            
                    for net in networkUris:
                        netName             = net.strip(' ')
                        netVar              = 'var_' + netName.lower().strip().replace('-', '_') 

                        if isEthernet:
                            scriptCode.append("                                                     "                                                                   )
                            scriptCode.append("     - name: Get uri for network {0}             ".format(netName)                                                       )
                            scriptCode.append("       oneview_ethernet_network_facts:           "                                                                       )
                            scriptCode.append("         config: \'{{config}}\'                  "                                                                       )
                            scriptCode.append("         name:   \'{}\'                          ".format(netName)                                                       )    
                            scriptCode.append("     - set_fact:                                 "                                                                       )
                            scriptCode.append("          {}: ".format(netVar)  + "\'{{ethernet_networks.uri}}\' "                                                       )  
                            scriptCode.append(CR)

                        if isFC:
                            scriptCode.append("                                                     "                                                                   )
                            scriptCode.append("     - name: Get uri for network {0}             ".format(netName)                                                       )
                            scriptCode.append("       oneview_fc_network_facts:                 "                                                                       )
                            scriptCode.append("         config: \'{{config}}\'                  "                                                                       )
                            scriptCode.append("         name:   \'{}\'                          ".format(netName)                                                       )    
                            scriptCode.append("     - set_fact:                                 "                                                                       )
                            scriptCode.append("          {}: ".format(netVar)  + "\'{{fc_networks[0].uri}}\' "                                                          )  
                            scriptCode.append(CR)

                        if 'fcoe' == networkType:
                            scriptCode.append("                                                     "                                                                   )
                            scriptCode.append("     - name: Get uri for network {0}             ".format(netName)                                                       )
                            scriptCode.append("       oneview_fcoe_network_facts:               "                                                                       )
                            scriptCode.append("         config: \'{{config}}\'                  "                                                                       )
                            scriptCode.append("         name:   \'{}\'                          ".format(netName)                                                       )    
                            scriptCode.append("     - set_fact:                                 "                                                                       )
                            scriptCode.append("          {}: ".format(netVar)  + "\'{{fcoe_networks.uri}}\' "                                                           )  
                            scriptCode.append(CR)

                # Define var for native network #####  Do I need this?
        

                if nativeNetworkUri:
                    netName             = nativeNetworkUri.strip(' ')
                    netVar              = 'var_' + netName.lower().strip().replace('-', '_')  

                    scriptCode.append("                                                     "                                                                   )
                    scriptCode.append("     - name: Get uri for native network {0}      ".format(netName)                                                       )
                    scriptCode.append("       oneview_ethernet_network_facts:           "                                                                       )
                    scriptCode.append("         config:     \'{{config}}\'              "                                                                       )
                    scriptCode.append("         name:       \'{}\'                      ".format(netName)                                                       )    
                    scriptCode.append("     - set_fact:                                 "                                                                       )  
                    scriptCode.append("          {}= ".format(netVar)  + "\'{{ethernet_networks.uri}}\' "                                                       )


                # Define var for port number
                
                if upl_logicalPortConfigs:
                    arr_logicalPortInfos            = build_logicalPortConfig_Array(upl_logicalPortConfigs,isFC, fabricModuleType)
                    for config in arr_logicalPortInfos:
                        ic_location         = config["ic_location"]
                        portName            = config["portName"]
                        var_portName        = portName.replace(':','_')
                        portNumber          = config["portNumber"]
                        enclosureIndex      = config["enclosureIndex"]
                        bay                 = config["bay"].lower().replace("bay","")

                        scriptCode.append("     - set_fact:        "                                                                                                 )
                        scriptCode.append("          var_{0}_{1}:   {2}".format(ic_location, var_portName, portNumber)                                               )




            # 2 -  open uplink set sheet to create uplink set

            currentLig                  = ""
            uplsheet.dropna(how='all', inplace=True)
            uplsheet                       = uplsheet.applymap(str)                       # Convert data frame into string
            
            for i in uplsheet.index:
                row                     = uplsheet.loc[i]
                name                    = row["name"]
                ligName                 = row['ligName']
                fabricModuleType        = row["fabricModuleType"]

                upl_logicalPortConfigs  = row["logicalPortConfigInfos"]     
                fcUplinkSpeed           = row['fcUplinkSpeed']              if  row["fcUplinkSpeed"]                            else 'Auto'  
                nativeNetworkUri        = row["nativeNetwork"]              
                networkUris             = row["networks"]                      # Ex: rhosp3_storage|Vlan3100-1|Vlan_501|rhosp3_storage_mgmt
                networkSetUris          = row["networkSets"]                   # Ex: rhosp3_storage|Vlan3100-1|Vlan_501|rhosp3_storage_mgmt
                
                networkType             = row["networkType"]
                lacpTimer               = row["lacpTimer"]                    
                loadBalancingMode       = row["loadBalancingMode"]          if  row["loadBalancingMode"]               else 'None'  
                mode                    = row["ethMode"]                    if  row["ethMode"]                         else 'Auto'

                trunking                = 'true'                            if  row['enableTrunking']                  else 'false'
                
                                

                networkType             = uplinkSetNetworkType[networkType]
                fcUplinkSpeed           = setUplinkSetPortSpeeds[fcUplinkSpeed]
                isFC                    = 'FibreChannel' == networkType
                isEthernet              = not isFC                

                
                # Configure Tagged/unTagged.Tunnel for Ethernet
                if isEthernet:
                    ethernetNetworkType = uplinkSetEthernetNetworkType[networkType]


                
                if currentLig != ligName:
                    scriptCode.append("                                                     "                                                                       )    
                    scriptCode.append("     - name: Create uplink set {0} for LIG --> {1}".format(name, ligName)                                                    )
                    scriptCode.append("       oneview_logical_interconnect_group:       "                                                                           )
                    scriptCode.append("         config:     \'{{config}}\'              "                                                                           )
                    scriptCode.append("         state:      present                     "                                                                           )
                    scriptCode.append("         data:                                   "                                                                           )
                    scriptCode.append("             name:                            {} ".format(ligName)                                                           )
                    scriptCode.append("             uplinkSets:                         "                                                                           )
                    # set new lig Name to be current
                    currentLig          = ligName

                scriptCode.append("               - name:                        {} ".format(name)                                                                  )
                #scriptCode.append("                 type:                        \'uplink-setV300\' "                            )
                scriptCode.append("                 mode:                        {} ".format(mode)                                                                  )
                scriptCode.append("                 networkType:                 {} ".format(networkType)                                                           )

                # LACP for Ethernet networks
                if not isFC:
                    scriptCode.append("                 ethernetNetworkType:         {} ".format(ethernetNetworkType)                                               )

                    if lacpTimer:
                        scriptCode.append("                 lacpTimer:                   {} ".format(lacpTimer)                                                     )
                        scriptCode.append("                 loadBalancingMode:           {} ".format(loadBalancingMode)                                             )
                else:
                    if 'true' in trunking:
                        scriptCode.append("                 fcMode:                        TRUNK "                                                                  )                

                # List of networks
                if networkUris:
                    networkUris         = networkUris.split('|')
                    scriptCode.append("                 networkUris:                "                                                                               )
                    for net in networkUris:
                        netName         = net.strip(' ')
                        netVar          = 'var_' + netName.lower().strip().replace('-', '_') 
                        netUri          = "\'{{" + '{}'.format(netVar) + "}}\'"
                        scriptCode.append("                     - {}                        ".format(netUri)                                                        )


                # List of networkSets
                if isEthernet and networkSetUris:
                    networkSetUris          = networkSetUris.split('|')
                    scriptCode.append("                 networkSetUris:                "                                                                           )
                    for netset in networkSetUris:
                        netsetName          = netset.strip(' ')
                        netsetName          = netsetName.lower().strip()
                        netsetVar           = 'var_' + netsetName.replace(' ', '_') 
                        
                        netsetUri           = "\'{{" + '{}'.format(netsetVar) + "}}\'"
                        scriptCode.append("                     - {}                        ".format(netsetUri)                                                   )


                # nativeNetworkUri

                if nativeNetworkUri:
                    netName             = nativeNetworkUri.strip(' ')
                    netVar              = 'var_' + netName.lower().strip().replace('-', '_') 
                    netUri          = "\'{{" + '{}'.format(netVar) + "}}\'"
                    scriptCode.append("                 nativeNetworkUri:               {} ".format(netUri)                                                       )


                # logicalPortInfos
                if upl_logicalPortConfigs:
                    scriptCode.append(CR)
                    scriptCode.append("                 logicalPortConfigInfos:                "                                                                 )

                    arr_logicalPortInfos            = build_logicalPortConfig_Array(upl_logicalPortConfigs,isFC, fabricModuleType)
                    for config in arr_logicalPortInfos:
                        ic_location         = config["ic_location"]
                        portName            = config["portName"]
                        portNumber          = config["portNumber"]
                        enclosureIndex      = config["enclosureIndex"]
                        bay                 = config["bay"].lower().replace("bay","")

                        var_portName        = portName.replace(':','_')                       
                        port_number         = "\'{{var_" + '{0}_{1}'.format(ic_location,var_portName) + "}}\'"     # port = '{{var_enclosure1_bay_3_portName}}' 
                                            

                    #scriptCode.append("                       - desiredFecMode:                 'Auto'     "                                 )
                        scriptCode.append("                       - desiredSpeed:                {}     ".format(fcUplinkSpeed)                                  )
                        scriptCode.append("                         logicalLocation:                    "                                                        )
                        scriptCode.append("                           locationEntries:                  "                                                        )    
                        scriptCode.append("                             - type:             \'Bay\'         "                                                    )
                        scriptCode.append("                               relativeValue:    {}              ".format(bay)                                        )
                        scriptCode.append("                             - type:             \'Port\'        "                                                    )
                        scriptCode.append("                               relativeValue:    {}              " .format(port_number)                               )
                        scriptCode.append("                             - type:             \'Enclosure\'   "                                                    )
                        scriptCode.append("                               relativeValue:    {}              " .format(enclosureIndex)                            )


        # end of LIG / uplinkset
        scriptCode.append("       delegate_to: localhost                    "                                                                                    )
        scriptCode.append(CR)





    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)





# ================================================================================================
#
#   generate_enclosure_groups_ansible_script
#
# ================================================================================================
def generate_enclosure_groups_ansible_script(sheet, to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                                  )
    scriptCode.append("- name:  Configure enclosure groups"                                                                                         )    
    build_header(scriptCode)

    ## Configure logical interconnect group
    scriptCode.append("  tasks:"                                                                                                                             )
    
    sheet       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                         = sheet.loc[i]
            name                        = row["name"]

            enclosureCount              = row["enclosureCount"]
            powerRedundantMode          = row["powerMode"]
            ligMappings                 = row['logicalInterConnectGroupMapping']        

            ipAddressingMode            = row['ipV4AddressingMode']                     if  row['ipV4AddressingMode']                       else 'DHCP'
            ipRangeUris                 = row['ipV4Range']                              
            ipV6AddressingMode          = row['ipV6AddressingMode']                     if  row['ipV6AddressingMode']                       else 'DHCP'
            ipV6RangeUris               = row['ipV6Range']                              
            scope                       = row['scopes']                                 

            ipAddressingMode            = ipAddressingMode.replace('AddressPool', 'IpPool')
            ipV6AddressingMode          = ipV6AddressingMode.replace('AddressPool', 'IpPool')

            if ligMappings:
                ligMappings         = ligMappings.split('|')
                for element in ligMappings:                                     # Frame1=LIG-ETH,LIG-SAS,LIG-FC
                    frame,lig_list  = element.split('=')
                    frame           = frame.strip(' ').lower()
                    lig_list        = lig_list.split(',')
                    for ligName in lig_list:
                        ligName     = ligName.strip(' ') 
                        lig_name    = ligName.replace('-', '_')                 # to be used in vars
                        scriptCode.append("     - set_fact:                                 "                                                                )
                        scriptCode.append("          IC_OFFSET:     3                       "                                                                )

                        scriptCode.append("                                                 "                                                                )
                        scriptCode.append("     - name: Get lig uri from  {0}               ".format(ligName)                                                )
                        scriptCode.append("       oneview_logical_interconnect_group_facts: "                                                                )
                        scriptCode.append("         config:    \'{{config}}\'               "                                                                )
                        scriptCode.append("         name:      \'{}\'                       ".format(ligName)                                                )
                        scriptCode.append("     - set_fact:         "                                                                                        )
                        scriptCode.append("         lig:       \'{{logical_interconnect_groups}}\' "                                                         )       
                        # if it's not lig then try with sas_lig
                        scriptCode.append("     - name: Try SAS lig for -->   {0}           ".format(ligName)                                                )
                        scriptCode.append("       oneview_sas_logical_interconnect_group_facts: "                                                            )
                        scriptCode.append("         config:    \'{{config}}\'               "                                                                )
                        scriptCode.append("         name:      \'{}\'                       ".format(ligName)                                                )
                        scriptCode.append("     - set_fact:         "                                                                                        )
                        scriptCode.append("         lig:       \'{{sas_logical_interconnect_groups}}\' "                                                     )   
                        scriptCode.append("       when: (lig|length == 0)                   "                                                                )

                        scriptCode.append(CR)
                        scriptCode.append("     - set_fact:         "                                                                                        )
                        scriptCode.append("          var_{0}_{1}_uri:      ".format(frame, lig_name) + "\'{{lig[0].uri}}\'"                                  )
                        scriptCode.append("          var_{0}_{1}_bay_primary: ".format(frame, lig_name) + "\'{{lig[0].interconnectBaySet}}\'"                )
                        scriptCode.append("          var_{0}_{1}_bay_secondary: ".format(frame, lig_name) + " \'{{lig[0].interconnectBaySet + IC_OFFSET}}\'" )
                        scriptCode.append(CR)


            # build ID pools uri if used
            var_range_names = []
            if ipAddressingMode == 'IpPool' and ipRangeUris:
                range_names     = ipRangeUris.split('|')

                for r_name in range_names: 
                    idpool_name     = r_name.lower().strip(' ').replace('-', '_')                 # to be used in vars        
                    var_name        = "var_{0}_uri   ".format(idpool_name)
                    var_range_names.append(var_name)
                    
                    scriptCode.append("                                                 "                                                             )
                    scriptCode.append("     - name: Get uri for range {}                ".format(r_name)                                              )
                    scriptCode.append("       oneview_id_pools_ipv4_range_facts:        "                                                             )
                    scriptCode.append("         config:     \'{{config}}\'              "                                                             )
                    scriptCode.append("     - set_fact:                                 "                                                             )
                    scriptCode.append("          {}:   ".format(var_name) + "\'{{item.uri}}\'"                                                        )
                    scriptCode.append("       loop:  \'{{id_pools_ipv4_ranges}}\'       "                                                             )
                    scriptCode.append("       when:  item.name == \'{}\'                ".format(r_name)                                              )

            scriptCode.append(CR)
            scriptCode.append("     - name: Create enclosure group {0}".format(name)                                                                  )
            scriptCode.append("       oneview_enclosure_group:                  "                                                                     )
            scriptCode.append("         config:    \'{{config}}\'               "                                                                     )
            scriptCode.append("         state:      present                     "                                                                     )
            scriptCode.append("         data:                                   "                                                                     )
            scriptCode.append("             name:                            {} ".format(name)                                                        )
            scriptCode.append("             enclosureCount:                  {} ".format(enclosureCount)                                              )
            scriptCode.append("             powerMode:                       {} ".format(powerRedundantMode)                                          )
        
            # Build interconnectBayMappings
            if ligMappings:
                scriptCode.append("             interconnectBayMappings: "                                                                            )

                for element in ligMappings:                                     # Frame1=LIG-ETH,LIG-SAS,LIG-FC
                    frame,lig_list  = element.split('=')
                    frame           = frame.strip(' ').lower()
                    lig_list        = lig_list.split(',')
                    for ligName in lig_list:
                        ligName     = ligName.strip(' ') 
                        lig_name    = ligName.replace('-', '_')                 # to be used in vars


                        lig_uri             = "{{" + "var_{0}_{1}_uri".format(frame, lig_name) + "}}"
                        var_bay_primary     = "{{" + "var_{0}_{1}_bay_primary".format(frame, lig_name) + "}}"
                        var_bay_secondary   = "{{" + "var_{0}_{1}_bay_secondary".format(frame, lig_name) + "}}"

                        enclosureIndex  = frame.strip('frameFrameenclosureEnclosure')

                        scriptCode.append("                 - interconnectBay:              \'{}\'      ".format(var_bay_primary)                                 )
                        scriptCode.append("                   logicalInterconnectGroupUri:  \'{}\'      ".format(lig_uri)                                         )
                        scriptCode.append("                   enclosureIndex:               {}          ".format(enclosureIndex)                                  )
                        scriptCode.append(CR)
                        scriptCode.append("                 - interconnectBay:               \'{}\'     ".format(var_bay_secondary)                               )
                        scriptCode.append("                   logicalInterconnectGroupUri:  \'{}\'      ".format(lig_uri)                                         )
                        scriptCode.append("                   enclosureIndex:               {}          ".format(enclosureIndex)                                  )
                        
            # Build ipv4 ranges

            scriptCode.append("")
            scriptCode.append("             ipAddressingMode:                {} ".format(ipAddressingMode)                                            )
            if var_range_names:
                scriptCode.append("             ipRangeUris: " )
                for idpool_name in var_range_names:
                    scriptCode.append("                 - \'{{" + "{0}".format(idpool_name.strip(' ')) +  "}}\' "                                     )

            # Add scope here
            
            if scope:
                netVar              = 'var_' + name.lower().strip().replace(',', '_').replace('-', '_').replace(' ', '')
                scriptCode.append("                                                             "                                                   )
                scriptCode.append("     - name: get logical enclosure                {}         ".format(name)                                      )
                scriptCode.append("       oneview_enclosure_group_facts:                        "                                                   )
                scriptCode.append("         config:     \'{{config}}\'                          "                                                   )
                scriptCode.append("         name:       \'{}\'                                  ".format(name)                                      )
                scriptCode.append("     - set_fact:                                             "                                                   )
                scriptCode.append("          {}: ".format(netVar)  + "\'{{enclosure_groups.uri}}\' "                                                )

                netUri              = "\'{{" + '{}'.format(netVar) + "}}\'"  

                generate_scope_for_resource(name, netUri, scope, scriptCode)




            # end of enclosure group
            scriptCode.append("       delegate_to: localhost                          "                                                                                 )
            scriptCode.append(CR)



    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)
                    


# ================================================================================================
#
#   generate_logical_enclosures_ansible_script
#
# ================================================================================================
def generate_logical_enclosures_ansible_script(sheet, to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                                           )
    scriptCode.append("- name:  Configure logical enclosures "                                                                                                        )    
    build_header(scriptCode)

    scriptCode.append("  tasks:"                                                                                                                                      )
    
    sheet       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                         = sheet.loc[i]
            name                        = row['name']                                    
            enclosureSerialNumber       = row['enclosureSerialNumber']                  
            enclosureName               = row['enclosureName']                          
            enclosureGroup              = row['enclosureGroup']                         
            fwBaseline                  = row['fwBaseline']                             
            fwInstall                   = row['fwInstall']                              if  row['fwInstall']                   else 'False'
            scope                       = row['scopes']                                  

            # Get enclosure Uris        
            if enclosureSerialNumber:
                list_enclosure          = enclosureSerialNumber.split('|')
                for enclosure in list_enclosure:
                    var_encl_name       = enclosure.replace('-','_')
                    scriptCode.append("                                                     "                                                                       )
                    scriptCode.append("     - name: Get uri of enclosure {}                 ".format(enclosure)                                                     )
                    scriptCode.append("       oneview_enclosure_facts:                      "                                                                       )
                    scriptCode.append("         config:            \'{{ config }}\'         "                                                                       )
                    scriptCode.append("     - set_fact:                                     "                                                                       )          
                    scriptCode.append("         list_enclosures : \'{{enclosures}}\'        "                                                                       )                               
                    scriptCode.append("     - set_fact:                                     "                                                                       )                                    
                    scriptCode.append("         var_{}_uri:       ".format(var_encl_name)   + "\'{{item.uri}}\'"                                                    )       
                    scriptCode.append("       loop: '{{list_enclosures}}'                   "                                                                       )
                    scriptCode.append("       when: item.name== \'{}\'                      ".format(enclosure)                                                     ) 


                # Get enclosure group Uris
                eg                      = enclosureGroup.strip().replace('-', '_').replace(' ', '_')
                var_eg_uri              = "var_{}_uri:   ".format(eg)
                scriptCode.append(CR)
                scriptCode.append("     - name: Get uri of enclosure group {}           ".format(enclosureGroup)                                                )
                scriptCode.append("       oneview_enclosure_group_facts:              "                                                                         )
                scriptCode.append("         config:   \'{{ config }}\'                  "                                                                       )
                scriptCode.append("         name:     {}                                ".format(enclosureGroup)                                                )
                scriptCode.append("     - set_fact:                                     "                                                                       )
                scriptCode.append("         var_{}_uri:   ".format(eg) + "\'{{enclosure_groups.uri}}\' "                                                        )
                scriptCode.append("")

                # Rename enclosure
                if enclosureName and enclosureSerialNumber:
                    list_enclosure          = enclosureSerialNumber.split('|')
                    list_name               = enclosureName.split('|')    
                    for index,sn in enumerate(list_enclosure):
                        scriptCode.append("     - name: Change name for enclosure {}            ".format(sn)                                                            )
                        scriptCode.append("       oneview_enclosure:                            "                                                                       )
                        scriptCode.append("         config:         \'{{ config }}\'            "                                                                       )
                        scriptCode.append("         state:          present                     "                                                                       )
                        scriptCode.append("         validate_etag:  False                       "                                                                       )
                        
                        scriptCode.append("         data:                               "                                                                       )
                        scriptCode.append("             name:       {}                  ".format(sn.strip())                                                    )
                        scriptCode.append("             newName:    {}                  ".format(list_name[index].strip())                                      )
                    
                # Create logical enclosure
                scriptCode.append(CR)
                scriptCode.append("     - name: Create logical enclosure {}             ".format(name)                                                          )
                scriptCode.append("       oneview_logical_enclosure:                    "                                                                       )
                scriptCode.append("         config:   \'{{ config }}\'                  "                                                                       )
                scriptCode.append("         state:     present                          "                                                                       )
                scriptCode.append("         data:                                       "                                                                       )
                scriptCode.append("             name:   \'{}\'                          ".format(name)                                                          )
                scriptCode.append("             enclosureGroupUri:  \'{{" + "var_{}_uri".format(eg) + "}}\'"                                                    )                                               
                scriptCode.append("             enclosureUris:                          "                                                                       )
                if enclosureSerialNumber:
                    list_enclosure          = enclosureSerialNumber.split('|')
                    for enclosure in list_enclosure:
                        var_encl_uri        = 'var_{}_uri'.format(enclosure.replace('-','_'))                                                                                      
                        scriptCode.append("                 -  \'{{" + var_encl_uri + "}}\'"                                                                    )                                        
                scriptCode.append(CR) 

                ## Add firmware 
                # Get fw Baseline Uris -
                if fwBaseline and 'true' in fwInstall.lower() :
                    fw                  = fwBaseline.strip().replace(' ','_').replace('-','_').lower()
                    fwInstall           = 'true' in fwInstall.lower()
                    scriptCode.append("                                                     "                                                                      )
                    scriptCode.append("     - name: Get uri of fw baseline {}               ".format(fwBaseline)                                                   )
                    scriptCode.append("       oneview_firmware_driver_facts:                "                                                                      )
                    scriptCode.append("         config:       \'{{ config }}\'              "                                                                      )
                    scriptCode.append("         name:         \'{}\'                        ".format(fwBaseline)                                                   )
                    scriptCode.append("     - set_fact:                                     "                                                                      )
                    scriptCode.append("         var_fw_{}_uri:   ".format(fw) + "\'{{firmware_drivers[0].uri}}\' "                                                 )
                    scriptCode.append("")


                    scriptCode.append("                                                     "                                                                      )
                    scriptCode.append("     - name: Update firmware on logical enclosure {} ".format(name)                                                         )
                    scriptCode.append("       oneview_logical_enclosure:                    "                                                                      )
                    scriptCode.append("         config:   \'{{ config }}\'                  "                                                                      )
                    scriptCode.append("         state:     firmware_updated                 "                                                                      )
                    scriptCode.append("         data:                                       "                                                                      )
                    scriptCode.append("             name:   \'{}\'                          ".format(name)                                                         )
                    scriptCode.append("             firmware:                               "                                                                      )
                    scriptCode.append("                 firmwareBaselineUri:                        \'{{" + "var_fw_{}_uri".format(fw) +  "}}\'"                   )
                    scriptCode.append("                 forceInstallFirmware:                       {}".format(fwInstall)                                          )
                    scriptCode.append("                 firmwareUpdateOn:                           \'EnclosureOnly\' "                                            )
                    scriptCode.append("                 validateIfLIFirmwareUpdateIsNonDisruptive:  true"                                                          )
                    scriptCode.append("                 logicalInterconnectUpdateMode:              \'Orchestrated\' "                                             )
                    scriptCode.append("                 updateFirmwareOnUnmanagedInterconnect:      true"                                                          )
                    scriptCode.append("             custom_headers:                         "                                                                      )                           
                    scriptCode.append("                 if-Match: \'*\'                     "                                                                      )

  
        
            # Add scope here
            
            if scope:
                netVar              = 'var_' + name.lower().strip().replace(',', '_').replace('-', '_').replace(' ', '')
                scriptCode.append("                                                             "                                                   )
                scriptCode.append("     - name: get logical enclosure                {}         ".format(name)                                      )
                scriptCode.append("       oneview_logical_enclosure_facts:                      "                                                   )
                scriptCode.append("         config:     \'{{config}}\'                          "                                                   )
                scriptCode.append("         name:       \'{}\'                                  ".format(name)                                      )
                scriptCode.append("     - set_fact:                                             "                                                   )
                scriptCode.append("          {}: ".format(netVar)  + "\'{{logical_enclosures.uri}}\' "                                              )

                netUri              = "\'{{" + '{}'.format(netVar) + "}}\'"  

                generate_scope_for_resource(name, netUri, scope, scriptCode)

        

                # end of logical enclosure 
                scriptCode.append("       delegate_to: localhost                        "                                                                           )
                scriptCode.append(CR)
            else:
                print(' No enclosure specified--> cannot create logical enclosure. Skip creating playbook for logical enclosure {}'.format(name))
        

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



# ================================================================================================
#
#   generate_profile_or_templates
#
# ================================================================================================
def generate_profile_or_template(values_in_dict,isProfile,scriptCode):

    # Coomon code for server profiles and templates

    isSpt                               = not isProfile
    prof                                = values_in_dict
    serverHardwareType                  = prof['serverHardwareType']                        
    enclosureGroupName                  = prof['enclosureGroupName']                        
    affinity                            = prof["affinity"]                                  if  prof['affinity']                           else 'Bay' 
    
    manageFirmware                      = prof['manageFirmware'].lower().capitalize()       if  prof['manageFirmware']                     else 'False' 
    firmwareBaselineName                = prof['firmwareBaselineName']                      
    firmwareInstallType                 = prof['firmwareInstallType']                       if  prof['firmwareInstallType']                else 'FirmwareOnlyOfflineMode'
    forceInstallFirmware                = prof['forceInstallFirmware']                      if  prof['forceInstallFirmware']               else 'False'
    firmwareActivationType              = prof['firmwareActivationType']                    if  prof['firmwareActivationType']             else  'NotScheduled'         # Values are: Immediate, Scheduled, NotScheduled
    firmwareSchedule                    = prof['firmwareSchedule']                          
    
    manageConnections                   = prof['manageConnections'].lower().capitalize()    if  prof['manageConnections']                  else 'False' 
    manageLocalStorage                  = prof['manageLocalStorage'].lower().capitalize()   if  prof['manageLocalStorage']                 else 'False' 
    manageSANStorage                    = prof['manageSANStorage'].lower().capitalize()     if  prof['manageSANStorage']                   else 'False'

    bm                 	                = prof["manageBootMode"].lower().capitalize()       if  prof['manageBootMode']                     else 'False' 
    bmMode                              = prof['mode']                                      if  prof['mode']                               else 'UEFI' 
    pxeBootPolicy                       = prof['pxeBootPolicy']                             if  prof['pxeBootPolicy']                      else 'Auto' 
    secureBoot                          = prof['secureBoot']                                if  prof['secureBoot']                         else 'Disabled' 
    bo                 	                = prof['manageBootOrder'].lower().capitalize()      if  prof['manageBootOrder']                    else 'False' 
    order                               = prof['order']                                     if  prof['order']                              else 'HardDisk' 
    
    manageBios                          = prof['manageBios'].lower().capitalize()           if  prof['manageBios']                         else 'False' 
    overriddenSettings                  = prof['overriddenSettings']                        
    
    manageMp                            = prof['manageMp'].lower().capitalize()             if  prof['manageMp']                           else 'False' 

    ##TB reviwed
    wwnType                             = prof["wwnType"]                                
    macType                             = prof["macType"]                               
    serialNumberType                    = prof["serialNumberType"]                      
    iscsiInitiatorNameType              = prof["iscsiInitiatorNameType"]                 
    hideUnusedFlexNics                  = prof["hideUnusedFlexNics"]                        if  prof['hideUnusedFlexNics']                  else 'False' 
    scope                               = prof['scopes']                                 

    sht                                 = serverHardwareType.strip().replace(' ', '_')
    



    if isSpt:
        fwConsistency 	                    = prof['firmwareConsistencyChecking'].lower()       
        if 'nan' == fwConsistency:
            fwConsistency                   = 'Unchecked'
        fwConsistency 		                = fwConsistency.replace('exact','Checked').replace('minimum', 'CheckedMinimum' ).replace('none', 'Unchecked')

        connConsistency                     = prof['connectionConsistencyChecking']
        if 'nan' == connConsistency:
            connConsistency                 = 'Unchecked'
        connConsistency 		            = connConsistency.replace('exact','Checked').replace('minimum', 'CheckedMinimum' ).replace('none', 'Unchecked')

        lsConsistency                       = prof['localStorageConsistencyChecking']
        bmConsistency                       = prof['bootModeConsistencyChecking']
        boConsistency                       = prof['bootOrderConsistencyChecking']
        biosConsistency                     = prof['biosConsistencyChecking']
        mpConsistency                       = prof['mpConsistencyChecking']


    var_sht                             = "\'{{" + "var_{}_uri".format(sht) + "}}\'"

    # Generate code
    scriptCode.append("             serverHardwareTypeUri:        {}            ".format(var_sht)                                                            )
    scriptCode.append("             enclosureGroupName:           {}            ".format(enclosureGroupName)                                                 )

    scriptCode.append("             affinity:                     {}            ".format(affinity)                                                           )

    scriptCode.append("             hideUnusedFlexNics:           {}            ".format(hideUnusedFlexNics)                                                 )
    if iscsiInitiatorNameType:
        scriptCode.append("             iscsiInitiatorNameType:      {}         ".format(iscsiInitiatorNameType)                                             )

    # types region
    if wwnType:
        scriptCode.append("             wwnType:                     {}         ".format(wwnType)                                                            )
    if macType:
        scriptCode.append("             macType:                     {}         ".format(macType)                                                            )
    if serialNumberType:
        scriptCode.append("             serialNumberType:            {}         ".format(serialNumberType)                                                   )
    if iscsiInitiatorNameType:
        scriptCode.append("             iscsiInitiatorNameType:      {}         ".format(iscsiInitiatorNameType)                                             )

    # bootMode region

    if 'True' in bm:
        scriptCode.append("             bootMode:                               "                                                                            )
        scriptCode.append("                 manageMode:              {}         ".format(bm)                                                                 )
        scriptCode.append("                 mode:                    {}         ".format(bmMode)                                                             )
        if 'BIOS' in bmMode.upper():
            scriptCode.append("                 secureBoot:              Disabled  "                                                                         )            
        if 'UEFI' == bmMode.upper():
            scriptCode.append("                 secureBoot:              Disabled   "                                                                        )    
            scriptCode.append("                 pxeBootPolicy:                   ".format(pxeBootPolicy)                                                     )   
        if 'optimized' in bmMode.lower():
            scriptCode.append("                 secureBoot:                      ".format(secureBoot)                                                        )    
            scriptCode.append("                 pxeBootPolicy:                   ".format(pxeBootPolicy)                                                     )                

        # boot order is allowed ONLY if managedMode is True

        if 'True' in bo and order:
            scriptCode.append("             boot:                                    "                                                                       )
            scriptCode.append("                 manageBoot:              {}          ".format(bo)                                                            )
            scriptCode.append("                 order:                               "                                                                       )

            for boot_order in order.split('|'):
                boot_order      = boot_order.strip(' ')
                scriptCode.append("                     - {}                         ".format(boot_order)                                                   )

    # BIOS settings

    if 'True' in manageBios and overriddenSettings:
        scriptCode.append("             bios:                                    "                                                                          )
        scriptCode.append("                 manageBios:               {}         ".format(manageBios)                                                       )
        scriptCode.append("                 overriddenSettings:                                    "                                                        )
        for setting in overriddenSettings.split('|'):                               # format is id=EnergyEfficientTurbo;value=Disabled|id=PowerRegulator;value=StaticHighPerf
            setting                         = setting.replace(CRLF,'').replace(CR,'')
            _id,value                       = setting.split(';')
            id_name,id_attribute            = _id.split('=')
            id_name                         = id_name.strip(' ')
            id_attribute                    = id_attribute.strip(' ')
            value_name, value_attribute     = value.split('=')
            value_name                      = value_name.strip(' ')
            value_attribute                 = value_attribute.strip(' ')
            scriptCode.append("                 - {0}:         {1}              ".format(id_name,id_attribute)                                          )
            scriptCode.append("                   {0}:      {1}                 ".format(value_name,value_attribute)                                    )

    # Firmware

        if 'True' in manageFirmware:
            forceInstallFirmware        = forceInstallFirmware.lower().capitalize()
            scriptCode.append("             firmware:                               "                                                                       )
            scriptCode.append("                 manageFirmware:          {}         ".format(manageFirmware)                                                )
            scriptCode.append("                 firmwareInstallType:     {}         ".format(firmwareInstallType)                                           )
            scriptCode.append("                 forceInstallFirmware:    {}         ".format(forceInstallFirmware)                                          )
            scriptCode.append("                 firmwareBaselineName:    {}         ".format(firmwareBaselineName)                                          )
            scriptCode.append("                 firmwareActivationType:  {}         ".format(firmwareActivationType)                                        )


# ================================================================================================
#
#   HELPER  for profile and templates -Add LOCAL Storage - Add Connections
#
# ================================================================================================

def generate_local_storage_for_profile(localstoragesheet,thisProfilename,isProfile,scriptCode):



    # -------------------------------- Local storage CSV
    currentProfileName              = ""
    columns_names                   = localstoragesheet.columns.tolist()
    localstoragesheet               = localstoragesheet.sort_values(columns_names[0])
    localstoragesheet               = localstoragesheet.applymap(str)                       # Convert data frame into string
    subsetlocalstoragesheet         = localstoragesheet[localstoragesheet[columns_names[0]]== thisProfilename]

    if not subsetlocalstoragesheet.empty:
        for i in subsetlocalstoragesheet.index:
            row                         = subsetlocalstoragesheet.loc[i]

            profileName                 = row['profileName'].strip()
            deviceSlot                  = row['deviceSlot'].strip()                              if  row['deviceSlot']          else 'Embedded' 
            mode                        = row['mode'].strip()                                    if  row['mode']                else 'Mixed'  
            driveWriteCache             = row['writeCache'].lower().capitalize().strip()         if  row['writeCache']          else 'Unmanaged' 
            initialize                  = row['initialize'].lower().capitalize().strip()         if  row['initialize']          else 'False' 


            ld_name                     = row['logicalDiskName']                                 
            storageLocation             = row['storageLocation']                                 if  row['storageLocation']     else 'Internal' 
            bootable                    = row['bootable'].lower().capitalize()                   if  row['bootable']            else 'False'
            driveSelectionBy            = row['driveSelectionBy']                                if  row['driveSelectionBy']    else 'SizeAndTechnology'
            driveTechnology             = row['driveType']                                       if  row['driveType']           else 'Auto' 
            maxDriveSize                = row['maxDriveSize']                                    if  row['maxDriveSize']        else '0' 
            minDriveSize                = row['minDriveSize']                                    if  row['minDriveSize']        else '0'          
            numPhysicalDrives           = row['numberofDrives']                                  if  row['numberofDrives']      else '0'            
            raidLevel                   = row['raidLevel']                                       
            accelerator                 = row['accelerator'].lower().capitalize()                if  row['accelerator']         else 'False'                                    
            eraseDataOnDelete           = row['eraseDataOnDelete'].lower().capitalize()          if  row['eraseDataOnDelete']   else 'False'

            driveTechnology             = driveTechnologyType[driveTechnology]                  # Set the correct type as in REST API

            # Generate Code
            if deviceSlot:

                if currentProfileName != profileName:
                    scriptCode.append("                                                     "                                                                   )
                    scriptCode.append("     - name: Add local storage \'{0}\' to server profile or template {1}    ".format(deviceSlot, profileName)            )
                    if isProfile:
                        scriptCode.append("       oneview_server_profile:                   "                                                                   )
                    else:
                        scriptCode.append("       oneview_server_profile_template:          "                                                                   )
                    scriptCode.append("         config:     \'{{ config }}\'                "                                                                   )
                    scriptCode.append("         state:      present                         "                                                                   )
                    scriptCode.append("         data:                                       "                                                                   )
                    scriptCode.append("             name:                          \'{}\'   ".format(profileName)                                               ) 
                    if isProfile:                 
                        scriptCode.append("             type:                          \'{}\'  ".format(rstype['serverprofile'])                                )
                    else:
                        scriptCode.append("             type:                          \'{}\'  ".format(rstype['serverprofiletemplate'])                        )

                    scriptCode.append("             localStorage:                           "                                                                   )
                    scriptCode.append("                 controllers:                        "                                                                   )
                    # set new profile name to be current
                    currentProfileName      = profileName

    
                scriptCode.append("                     - deviceSlot:           {}      ".format(deviceSlot)                                                ) 
                scriptCode.append("                       driveWriteCache:      {}      ".format(driveWriteCache)                                           )
                scriptCode.append("                       initialize:           {}      ".format(initialize)                                                )
                scriptCode.append("                       mode:                 {}      ".format(mode)                                                      )

                if ld_name:
                    scriptCode.append("                       logicalDrives:                "                                                               )
                    scriptCode.append("                         - name:                 {}  ".format(ld_name)                                               )    
                    scriptCode.append("                           accelerator:          {}  ".format(accelerator)                                           ) 
                    scriptCode.append("                           bootable:             {}  ".format(bootable)                                              )  
                    scriptCode.append("                           driveTechnology:      {}  ".format(driveTechnology)                                       )
                    scriptCode.append("                           numPhysicalDrives:    {}  ".format(numPhysicalDrives)                                     )
                    scriptCode.append("                           raidLevel:            {}  ".format(raidLevel)                                             )



def generate_connection_for_profile(connectionsheet,thisProfilename,isProfile,scriptCode):

        
    # -------------------------------- Network Connection CSV
    currentProfileName              = ""

    columns_names                   = connectionsheet.columns.tolist()
    connectionsheet                 = connectionsheet.sort_values(columns_names[0])
    connectionsheet                 = connectionsheet.applymap(str)                       # Convert data frame into string

    subsetconnectionsheet           = connectionsheet[connectionsheet[columns_names[0]]== thisProfilename]


    if not subsetconnectionsheet.empty:
        for i in subsetconnectionsheet.index:
            row                         = subsetconnectionsheet.loc[i]

            name                        = row['name']                                    
            profileName                 = row['profileName']
            id                          = row['id']                                     
            functionType                = row['functionType'].lower().capitalize()       
            networkUri                  = row['network']                                
            portId                      = row['portId']                                 
            requestedMbps               = row['requestedMbps']                          
            requestedVFs                = row['requestedVFs']                          
            lagName                     = row['lagName']                                

            userDefined                 = row['userDefined']
            userDefined                 = userDefined.lower().capitalize()
            if 'True' in userDefined:
                mac                     = row['mac']                                   
                wwwnn                   = row['wwnn']                                  
                wwpn                    = row['wwpn']                                   

            boot                        = row['boot'].lower().capitalize()              if  row['boot']            else 'False' 
            priority                    = row['priority']                               

            functionType                = functionType.replace('Fc', 'FibreChannel')

            if name:
                manageConnections       = True

            if currentProfileName != profileName:
                # create new play for connections
                scriptCode.append(CR)
                scriptCode.append("     - name: Add network connection \'{0}\'  to server profile or template {1}     ".format(networkUri, profileName)         )
                if isProfile:
                    scriptCode.append("       oneview_server_profile:                   "                                                                       )
                else:
                    scriptCode.append("       oneview_server_profile_template:          "                                                                       )
                scriptCode.append("         config:     \'{{ config }}\'                "                                                                       )
                scriptCode.append("         state:      present                         "                                                                       )
                scriptCode.append("         data:                                       "                                                                       )
                scriptCode.append("             name:                          \'{}\'   ".format(profileName)                                                   )    
                if isProfile:              
                    scriptCode.append("             type:                          \'{}\'   ".format(rstype['serverprofile'])                                   )
                else:
                    scriptCode.append("             type:                          \'{}\'   ".format(rstype['serverprofiletemplate'])                           )
                scriptCode.append("             connectionSettings:                     "                                                                       )
                if not isProfile:           # Only template has it
                    scriptCode.append("                 manageConnections:          {}      ".format(manageConnections)                                         )
                scriptCode.append("                 connections:                        "                                                                       )
                # set new profile name to be current
                currentProfileName      = profileName


            scriptCode.append("                     - id:                   {}      ".format(id)                                                                ) 
            scriptCode.append("                       portId:               {}      ".format(portId)                                                            ) 
            scriptCode.append("                       name:                 {}      ".format(name)                                                              ) 
            scriptCode.append("                       functionType:         {}      ".format(functionType)                                                      ) 
            scriptCode.append("                       networkName:          {}      ".format(networkUri)                                                        ) 

            if lagName:
                scriptCode.append("                       lagName:              {}      ".format(lagName)                                                       ) 
            if requestedVFs:
                scriptCode.append("                       requestedVFs:         {}      ".format(requestedVFs)                                                  ) 
            if requestedMbps:
                scriptCode.append("                       requestedMbps:        {}      ".format(requestedMbps)                                                 )

            # Bootable connection
            if 'True'in boot:
                scriptCode.append("                       boot:                     "                                                                           )
                scriptCode.append("                         priority:           {}      ".format(priority)                                                      )
                if 'Ethernet' in functionType:
                    scriptCode.append("                         ethernetBootType:   PXE  "                                                                      )

            ### mac/wwn
            if 'True' in userDefined:
                if mac and 'Ethernet' in functionType:
                    scriptCode.append("                       mac:                     \'{}\'      ".format(macAddress)                                        )
        
                if wwwnn and 'FibreChannel' in functionType:
                    scriptCode.append("                       wwwn:                      \'{}\'      ".format(wwwn)                                            )
                if wwwpn and 'FibreChannel' in functionType:
                    scriptCode.append("                       wwpn:                      \'{}\'      ".format(wwpn)                                            )





# ================================================================================================
#
#   generate_server_profile_templates_ansible_script
#
# ================================================================================================
def generate_server_profile_templates_ansible_script(sheet,connectionsheet,localstoragesheet, to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                                 )
    scriptCode.append("- name:  Creating server profile templates from csv"                                                                                 )    
    build_header(scriptCode)

    scriptCode.append("  tasks:"                                                                                                                            )
    sheet       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                         = sheet.loc[i]

            name                        = row['name']                                   
            description                 = row['description']                            
            serverProfileDescription    = row['serverProfileDescription']               
            scope                       = row['scopes']                                 
            serverHardwareType          = row['serverHardwareType']                      



            if name:
                # ---- Set variables
                # Get server hardwareType Uris
                sht                     = serverHardwareType.strip().replace(' ', '_')
                var_sht                 = "var_{}_uri    ".format(sht) 
                scriptCode.append(CR)
                scriptCode.append("     - name: Get uri of serverhardware type {}       ".format(serverHardwareType)                                            )
                scriptCode.append("       oneview_server_hardware_type_facts:           "                                                                       )
                scriptCode.append("         config:   \'{{ config }}\'                  "                                                                       )
                scriptCode.append("         name:     {}                                ".format(serverHardwareType)                                            )
                scriptCode.append("     - set_fact:                                     "                                                                       )
                scriptCode.append("         {}:       ".format(var_sht) + "\'{{server_hardware_types[0].uri}}\' "                                               )
                scriptCode.append(CR)


                # Create server profile template
                scriptCode.append(CR)
                scriptCode.append("     - name: Create server profile template {}       ".format(name)                                                          )
                scriptCode.append("       oneview_server_profile_template:              "                                                                       )
                scriptCode.append("         config:     \'{{ config }}\'                "                                                                       )
                scriptCode.append("         state:      present                         "                                                                       )
                scriptCode.append("         data:                                       "                                                                       )

                scriptCode.append("             name:                       \'{}\'      ".format(name)                                                          )
                scriptCode.append("             type:                       \'{}\'      ".format(rstype['serverprofiletemplate'])                               )
                scriptCode.append("             description:                \'{}\'      ".format(description)                                                   )
                scriptCode.append("             serverProfileDescription:   \'{}\'      ".format(serverProfileDescription)                                      )

                # Add profile attributes
                isProfile   = False
                generate_profile_or_template(row,isProfile,scriptCode)

                # Add network connections
                if not connectionsheet.empty:
                    generate_connection_for_profile(connectionsheet,name,isProfile,scriptCode) 

                # Add network connections
                if not localstoragesheet.empty:
                    generate_local_storage_for_profile(localstoragesheet,name,isProfile,scriptCode) 

                # Add scope
                if scope:
                    netVar              = 'var_' + name.lower().strip().replace(',', '_').replace('-', '_').replace(' ', '') 
                    scriptCode.append(CR)
                    scriptCode.append("     - name: get spt                {}                       ".format(name)                                      )
                    scriptCode.append("       oneview_server_profile_template_facts:                "                                                   )
                    scriptCode.append("         config:     \'{{config}}\'                          "                                                   )
                    scriptCode.append("         name:       \'{}\'                                  ".format(name)                                      )
                    scriptCode.append("     - set_fact:                                             "                                                   )
                    scriptCode.append("          {}: ".format(netVar)  + "\'{{server_profile_templates[0].uri}}\' "                                     )

                    netUri              = "\'{{" + '{}'.format(netVar) + "}}\'"  
                    generate_scope_for_resource(name, netUri, scope, scriptCode)
        

        



    # end of server profile template
    scriptCode.append("       delegate_to: localhost                    "                                                                       )
    scriptCode.append(CR)
    #print(CR.join(scriptCode))

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



# ================================================================================================
#
#   generate_server_profiles_ansible_script
#
# ================================================================================================
def generate_server_profiles_ansible_script(sheet,connectionsheet,localstoragesheet, to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                               )
    scriptCode.append("- name:  Creating server profiles         "                                                                                        )    
    build_header(scriptCode)

    ##
    scriptCode.append("  tasks:"                                                                                                                          )
    sheet       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                         = sheet.loc[i]

            name                        = row['name']                               
            description                 = row['description']                        
            serverProfileTemplateUri    = row['serverProfileTemplate'].strip()                               
            serverHardwareUri           = row['serverHardware'].strip()                     if  row['serverHardware']              else 'unassigned'       
            scope                       = row['scopes']                             

            if name:
                name            = name.strip()
                scriptCode.append("# ---------------- Create server profile {}         ".format(name)                                                               )
                # Get server hardware URI from name
                var_hardware_uri            = 'unassigned'
                if 'unassigned' != serverHardwareUri.lower():
                    var_hardware_name        = serverHardwareUri.strip().replace(',', '_').replace('-', '_').replace(' ', '') 
                    var_hardware_uri         = "var_{}_uri".format(var_hardware_name)
                    scriptCode.append(CR)
                    scriptCode.append("     - name: Get server hardware uri   {}            ".format(serverHardwareUri)                                             )
                    scriptCode.append("       oneview_server_hardware_facts:                "                                                                       )
                    scriptCode.append("         config:             \'{{ config }}\'        "                                                                       )
                    scriptCode.append("         name:                \'{}\'                 ".format(serverHardwareUri)                                             )    
                    scriptCode.append("     - set_fact:                                     "                                                                       )
                    scriptCode.append("         {}:                 ".format(var_hardware_uri) + "\'{{server_hardwares.uri}}\' "                                    )  
                    scriptCode.append(CR)                



                    # Power off the server 
                    scriptCode.append("     - name: Power off server {}                     ".format(serverHardwareUri)                                                 )
                    scriptCode.append("       oneview_server_hardware:                      "                                                                           )
                    scriptCode.append("         config:     \'{{ config }}\'                "                                                                           )
                    scriptCode.append("         state:      power_state_set                 "                                                                           )
                    scriptCode.append("         data:                                       "                                                                           )
                    scriptCode.append("             name:                           \'{}\'  ".format(serverHardwareUri)                                                 )
                    scriptCode.append("             powerStateData:                         "                                                                           ) 
                    scriptCode.append("                 powerState: \'Off\'                 "                                                                           )
                    scriptCode.append("                 powerControl: \'MomentaryPress\'    "                                                                           )
                    scriptCode.append("                                                     "                                                                           )

                if not serverProfileTemplateUri:
                    # Create standalone profile
                    scriptCode.append("     - name: Create server profile {0}               ".format(name)                                                              )
                    scriptCode.append("       oneview_server_profile:                       "                                                                           )
                    scriptCode.append("         config:     \'{{ config }}\'                "                                                                           )
                    scriptCode.append("         state:      present                         "                                                                           )
                    scriptCode.append("         data:                                       "                                                                           )
                    scriptCode.append("             name:                           \'{}\'  ".format(name)                                                              )
                    scriptCode.append("             type:                           \'{}\'  ".format(rstype['serverprofile'])                                           )
                    scriptCode.append("             description:                    \'{}\'      ".format(description)                                                   )
                    
                    isProfile   = True
                    # Add attributes to profile
                    generate_profile_or_template(row, isProfile, scriptCode)
                    # Addd network connections and storage
                    
                    generate_connection_storage_for_profile(connectionsheet,localstoragesheet,name,isProfile,scriptCode) 

                # Create profile from template
                else:               
                    var_template_name           = serverProfileTemplateUri.strip().replace(',', '_').replace('-', '_').replace(' ', '') 
                
                    # Get template uri from name
                    scriptCode.append(CR)
                    scriptCode.append("     - name: Get profile template uri   {}           ".format(serverProfileTemplateUri)                                          )
                    scriptCode.append("       oneview_server_profile_template_facts:        "                                                                           )
                    scriptCode.append("         config:             \'{{ config }}\'        "                                                                           )
                    scriptCode.append("         name:                \'{}\'                 ".format(serverProfileTemplateUri)                                          )     
                    scriptCode.append("     - set_fact:                                     "                                                                           )
                    scriptCode.append("         var_{}_uri:   ".format(var_template_name) + "\'{{server_profile_templates[0].uri}}\' "                                  )    
                    scriptCode.append(CR)


                    # Create server profile from template
                    scriptCode.append("     - name: Create server profile {0} from template {1} ".format(name, serverProfileTemplateUri)                                )
                    scriptCode.append("       oneview_server_profile:                       "                                                                           )
                    scriptCode.append("         config:     \'{{ config }}\'                "                                                                           )
                    scriptCode.append("         state:      present                         "                                                                           )
                    scriptCode.append("         data:                                       "                                                                           )
                    scriptCode.append("             name:                           \'{}\'  ".format(name)                                                              )
                    scriptCode.append("             type:                           \'{}\'  ".format(rstype['serverprofile'])                                           )
                    if 'nan' != description:
                        scriptCode.append("             description:                    \'{}\'      ".format(description)                                               )

                    var_template_uri                = "var_{}_uri".format(var_template_name) 
                    scriptCode.append("             serverProfileTemplateUri:       \'{{"   + "{}".format(var_template_uri)  + "}}\'"                                   )
                    scriptCode.append("             serverHardwareUri:              \'{{"   + "{}".format(var_hardware_uri)  + "}}\'"                                   )
                    scriptCode.append(CR)


                
                # Add scope
                if  scope:
                    netVar              = 'var_' + name.lower().strip().replace(',', '_').replace('-', '_').replace(' ', '') 
                    scriptCode.append(CR)
                    scriptCode.append("     - name: get server profile  {}                          ".format(name)                                      )
                    scriptCode.append("       oneview_server_profile_facts:                         "                                                   )
                    scriptCode.append("         config:     \'{{config}}\'                          "                                                   )
                    scriptCode.append("         name:       \'{}\'                                  ".format(name)                                      )
                    scriptCode.append("     - set_fact:                                             "                                                   )
                    scriptCode.append("          {}: ".format(netVar)  + "\'{{server_profiles[0].uri}}\' "                                              )

                    netUri              = "\'{{" + '{}'.format(netVar) + "}}\'"  
                    generate_scope_for_resource(name, netUri, scope, scriptCode)



                # Power on the server 
                if 'unassigned' != serverHardwareUri.lower():
                    scriptCode.append("     - name: Power on server {}                     ".format(serverHardwareUri)                                                  )
                    scriptCode.append("       oneview_server_hardware:                      "                                                                           )
                    scriptCode.append("         config:     \'{{ config }}\'                "                                                                           )
                    scriptCode.append("         state:      power_state_set                 "                                                                           )
                    scriptCode.append("         data:                                       "                                                                           )
                    scriptCode.append("             name:                           \'{}\'  ".format(serverHardwareUri)                                                 )
                    scriptCode.append("             powerStateData:                         "                                                                           ) 
                    scriptCode.append("                 powerState: \'On\'                  "                                                                           )
                    scriptCode.append("                 powerControl: \'MomentaryPress\'    "                                                                           )
                    scriptCode.append(CR)


        
        # end of server profile
        scriptCode.append("       delegate_to: localhost                    "                                                                                       )
        scriptCode.append(CR)

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)



# ================================================================================================
#
#   generate_san_manager_ansible_script
#
# ================================================================================================
def generate_san_manager_ansible_script(sheet, to_file):
    

    authLevel           = {
        'none'          : 'none',
        'authonly'      : 'authnopriv',
        'authandpriv'   : 'authpriv'
    }
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                               )
    scriptCode.append("- name:  Creating san manager             "                                                                                        )    
    build_header(scriptCode)

    ##
    scriptCode.append("  tasks:"                                                                                                                          )
    sheet       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                         = sheet.loc[i]

            _type                       = row['type'].strip()
            name                        = row['name'].strip()  
            port                        = row["port"].strip()                             

            if _type:
                _type                   = _type.capitalize()
                if 'Brocade' in _type or 'Bna' in _type:
                    _type               = 'Brocade Network Advisor'
                
                    userName            = row["userName"].strip()
                    password            = row["password"].strip()
                    useSSL              = row["useSSL"].capitalize() if row["useSSL"]   	else 'False' 
                else:
                    snmpUserName        = row["snmpUserName"].strip()
                    snmpAuthLevel       = row["snmpAuthLevel"].strip().lower()
                    snmpAuthProtocol    = row["snmpAuthProtocol"].strip()
                    snmpAuthPassword    = row["snmpAuthPassword"].strip()
                    snmpPrivProtocol    = row["snmpPrivProtocol"].strip()
                    snmpPrivPassword    = row["snmpPrivPassword"].strip()



                scriptCode.append("     - name: Create san manager                      "                                                                           )
                scriptCode.append("       oneview_san_manager:                          "                                                                           )
                scriptCode.append("         config:     \'{{ config }}\'                "                                                                           )
                scriptCode.append("         state:      present                         "                                                                           )
                scriptCode.append("         data:                                       "                                                                           )
                scriptCode.append("             name:                           \'{}\'  ".format(name)                                                              ) 
                scriptCode.append("             providerDisplayName:             {}     ".format(_type)                                                             )
                scriptCode.append("             connectionInfo:                         "                                                                           )
                scriptCode.append("                 - name:                      Host   "                                                                           )
                scriptCode.append("                   value:                     \'{}\' ".format(name)                                                              )
                
                if 'Brocade' in _type:
                    scriptCode.append("                 - name:                      Port     "                                                                         )
                    scriptCode.append("                   value:                     {}       ".format(port)                                                            )
                    scriptCode.append("                 - name:                      UserName "                                                                         )
                    scriptCode.append("                   value:                     \'{}\' ".format(userName)                                                          )
                    scriptCode.append("                 - name:                      Password "                                                                         )
                    scriptCode.append("                   value:                     \'{}\' ".format(password)                                                          )
                    scriptCode.append("                 - name:                      UseSSL "                                                                           )
                    scriptCode.append("                   value:                     {}     ".format(useSSL)                                                            )

                else:     
                    scriptCode.append("                 - name:                      SnmpPort "                                                                         )
                    scriptCode.append("                   value:                     {}       ".format(port)                                                            )
                    scriptCode.append("                 - name:                      SnmpUserName "                                                                     )
                    scriptCode.append("                   value:                     \'{}\'   ".format(snmpUserName)                                                    )
                    scriptCode.append("                 - name:                      SnmpAuthLevel "                                                                    )
                    scriptCode.append("                   value:                     \'{}\' ".format(authLevel[snmpAuthLevel] )                                         )
                    scriptCode.append("                 - name:                      SnmpAuthProtocol "                                                                 )
                    scriptCode.append("                   value:                     \'{}\' ".format(snmpAuthProtocol)                                                  )
                    scriptCode.append("                 - name:                      SnmpAuthString "                                                                   )
                    scriptCode.append("                   value:                     \'{}\' ".format(snmpAuthPassword)                                                  )
                    scriptCode.append("                 - name:                      SnmpPrivProtocol "                                                                 )
                    scriptCode.append("                   value:                     \'{}\' ".format(snmpPrivProtocol)                                                  )
                    scriptCode.append("                 - name:                      SnmpPrivString "                                                                   )
                    scriptCode.append("                   value:                     \'{}\' ".format(snmpPrivPassword)                                                  )
                
                scriptCode.append(CR)




        # end of san Manager
        scriptCode.append("       delegate_to: localhost                    "                                                                                       )
        scriptCode.append(CR)

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


# ================================================================================================
#
#   generate_storage_system_ansible_script
#
# ================================================================================================
def generate_storage_system_ansible_script(sheet, to_file):
		

    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                               )
    scriptCode.append("- name:  Creating storage System          "                                                                                        )    
    build_header(scriptCode)

    ##
    scriptCode.append("  tasks:"                                                                                                                          )
    sheet       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        for i in sheet.index:
            row                         = sheet.loc[i]

            name                        = row['name'].strip()  
            family                      = row['family'].strip()
            domain                      = row['domain'].strip()                             if row['domain']    	        else 'NO DOMAIN'
            userName                    = row["userName"].strip()
            password                    = row["password"].strip()
            portGroups                  = row["portGroups"].strip()    
            ports                       = row["ports"].strip()    
            vips                        = row["vips"].strip()  
            showSystemDetails           = row["showSystemDetails"].lower().capitalize()     if row["showSystemDetails"]   	else 'False'    
            storagePool                 = row["storagePool"].strip()                    

            scriptCode.append("     - name: Create storage systems                  "                                                                           )
            scriptCode.append("       oneview_storage_system:                       "                                                                           )
            scriptCode.append("         config:     \'{{ config }}\'                "                                                                           )
            scriptCode.append("         state:      present                         "                                                                           )
            scriptCode.append("         data:                                       "                                                                           )
            scriptCode.append("             hostname:                       \'{}\'  ".format(name)                                                              ) 
            scriptCode.append("             family:                         {}      ".format(family)                                                            )
            scriptCode.append("             credentials:                            "                                                                           )
            scriptCode.append("                 - username:                 {}      ".format(userName)                                                          )
            scriptCode.append("                   password:                 {}      ".format(password)                                                          )


           # end of storage Systems
        scriptCode.append("       delegate_to: localhost                    "                                                                            )
        scriptCode.append(CR)

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file) 



# ================================================================================================
#
#   generate_inventory_file_ansible_script
#
# ================================================================================================
def generate_inventory_file_ansible_script(inventory_file,to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                               )
    scriptCode.append("- name:  Creating inventory file"                                                                                                  )    
    build_header(scriptCode)

    ##
    scriptCode.append("  tasks:"                                                                                                                          )
    scriptCode.append("     - name: Create inventory file {}                ".format(inventory_file)                                                      )
    scriptCode.append("       copy:                                         "                                                                             )
    scriptCode.append("         dest:           {}                          ".format(inventory_file)                                                      )
    scriptCode.append("         content:        server profile,portId,MAC,wwnn,wwpn"                                                                      )
    # end 
    scriptCode.append("       delegate_to: localhost                        "                                                                             )
    scriptCode.append(CR)

    # ============= Write scriptCode ====================
    write_to_file(scriptCode, to_file)


# ================================================================================================
#
#   generate_inventory_sp_ansible_script
#
# ================================================================================================
def generate_inventory_sp_ansible_script(sheet,inventory_file, to_file):
    
    print('Creating ansible playbook   =====>           {}'.format(to_file))    
    scriptCode = []
    scriptCode.append("---"                                                                                                                               )
    scriptCode.append("- name:  Inventory of mac,wwnn and wwpn for server profile"                                                                        )    
    build_header(scriptCode)

    ##
    scriptCode.append("  tasks:"                                                                                                                          )
    
    sheet       = sheet.applymap(str)                       # Convert data frame into string
    if not sheet.empty:
        scriptCode.append("     - name: Create inventory file {}                ".format(inventory_file)                                                      )
        scriptCode.append("       copy:                                         "                                                                             )
        scriptCode.append("         dest:           {}                          ".format(inventory_file)                                                      )
        scriptCode.append("         content:        server profile,portId,MAC,wwnn,wwpn"                                                                      )

        for i in sheet.index:
            row                         = sheet.loc[i]

            name                        = row['name'].strip()                               if  'nan' != row['name']                        else ''
 
            if name:         
                scriptCode.append(CR)
                scriptCode.append("     - name: Collect mac,wwnn,wwpn on profile {}     ".format(name)                                                          )
                scriptCode.append("       oneview_server_profile_facts:                 "                                                                       )
                scriptCode.append("         config:     \'{{ config }}\'                "                                                                       )
                scriptCode.append("         name:       \'{}\'                          ".format(name)                                                          )
                scriptCode.append("     - set_fact:                                     "                                                                       )
                scriptCode.append("         var_spName: \'{}\'                          ".format(name)                                                          )
                scriptCode.append("         var_connections: \'{{ server_profiles[0].connectionSettings.connections }}\'"                                       )
                scriptCode.append("     - lineinfile:                                     "                                                                     )
                scriptCode.append("         path:          {}                           ".format(inventory_file)                                                )
                scriptCode.append("         line:          \'{{var_spName}},{{item.portId}},{{item.mac}},{{item.wwnn}},{{item.wwpn}}\'"                         )           
                scriptCode.append("       loop:  \'{{var_connections}}\'                "                                                                       )



        # end of update 
        scriptCode.append("       delegate_to: localhost                            "                                                                       )
        scriptCode.append(CR)


        # ============= Write scriptCode ====================
        write_to_file(scriptCode, to_file)

# ================================================================================================
#
#   initialize_mainplaybook_file
#
# ================================================================================================
def add_to_allScripts(text, ymlFile):
    allScriptCode.append('# {}'.format(text) )

    allScriptCode.append("echo -------" )
    allScriptCode.append("echo         {} ".format(text) )
    allScriptCode.append("echo -------" )
    allScriptCode.append("echo")
    allScriptCode.append('ansible-playbook  {}'.format(ymlFile))
    allScriptCode.append(CR )


# ================================================================================================
#
#   MAIN
#
# ================================================================================================


if __name__ == "__main__":
    _home = os.getcwd()

    # Read excel file
    if len(sys.argv) >= 2:
        excelfile        = sys.argv[1]
        
    else:
        print('No Excel file specified. Exiting now....')
        sys.exit()

    print(CR)




    #xl = pd.read_excel(excelfile, None)
    xl                      = pd.ExcelFile(excelfile)


    versionsheet            = composersheet = pd.DataFrame()
    usersheet               = timelocalesheet = backupconfigsheet = firmwaresheet = snmpsheet = addresspoolsheet = scopesheet = pd.DataFrame()
    ethernetnetworksheet    = fcnetworksheet = networksetsheet = pd.DataFrame()
    ligsheet                = ligsnmpsheet = uplinksetsheet  = pd.DataFrame()
    enclosuregroupsheet     = logicalenclosuresheet = pd.DataFrame() 
    profilesheet            = profiletemplatesheet = profileconnectionsheet  = profilelocalstoragesheet = profilesanstoragesheet  = profileilosheet = pd.DataFrame()
    sanmanagersheet          = storagesystemsheet = pd.DataFrame()

    for sheet in xl.sheet_names:
        sheet_name          = sheet.lower()
        if 'version' == sheet_name:
            versionsheet                        = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')
        if 'composer' == sheet_name:
            composersheet                       = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')

        # OV Resources    

        if 'user' == sheet_name:
            usersheet                           = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')        
        if 'timelocale' == sheet_name:
            timelocalesheet                     = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')
        if 'backup' == sheet_name:
            backupconfigsheet                   = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')
        if 'firmwarebaseline' == sheet_name:
            firmwaresheet                       = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')
        if 'snmpv1' == sheet_name:
            snmpsheet                           = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')
        if 'addresspool' == sheet_name:
            addresspoolsheet                    = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')

        if 'scope' == sheet_name:
            scopesheet                          = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')

        if 'ethernetnetwork' == sheet_name:
            ethernetnetworksheet                = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')   

        if 'fcnetwork' == sheet_name:
            fcnetworksheet                      = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')
        if 'networkset' == sheet_name:
            networksetsheet                     = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')


        if 'logicalinterconnectgroup' == sheet_name:
            ligsheet                            = pd.read_excel(excelfile, sheet  ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')

        if 'uplinkset' == sheet_name:
            uplinksetsheet                      = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')           

        if 'lig-snmp' == sheet_name:
            ligsnmpsheet                        = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')   

        if 'sanmanager' == sheet_name:
            sanmanagersheet                     = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')   

        if 'storagesystem' == sheet_name:
            storagesystemsheet                  = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('') 

        if 'enclosuregroup' == sheet_name:
            enclosuregroupsheet                 = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')
        if 'logicalenclosure' == sheet_name:
            logicalenclosuresheet               = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')
      
        if 'profiletemplate' == sheet_name:
            profiletemplatesheet                = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')

        if 'profile' == sheet_name:
            profilesheet                        = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')

        if 'profileconnection' == sheet_name:
            profileconnectionsheet              = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')

        if 'profilelocalstorage' == sheet_name:
            profilelocalstoragesheet            = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')

        if 'profilesanstorage' == sheet_name:
            profilesanstoragesheet              = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')

        if 'profileilo' == sheet_name:
            profileilosheet                     = pd.read_excel(excelfile, sheet   ,comment='#' , dtype=str).dropna(how='all', inplace=False).fillna('')



    # Generate prefix  - NOT USED NOW
    # prefix  = generate_ansible_configuration(versionsheet)


    # Create YML parent folder
    ymlFolder           = _home + '/playbooks/'
    if not os.path.isdir(ymlFolder):
        os.makedirs(ymlFolder)
    
    #  Generate OneView config json
    print('#---------------- Generate ansible configuration ')
    config_file =  ymlFolder + 'oneview_config.json'   
    generate_oneview_config_configuration(composersheet, config_file)

    # Create YML sub folders that mirrors OneView structure
    subFolder      = ymlFolder + 'settings/'
    if not os.path.isdir(subFolder):
        os.makedirs(subFolder)
    shutil.copy(config_file, subFolder)         # copy oneview_config.json

    subFolder      = ymlFolder + 'appliance/'
    if not os.path.isdir(subFolder):
        os.makedirs(subFolder)
    shutil.copy(config_file, subFolder)         # copy oneview_config.json

    subFolder      = ymlFolder + 'networking/'
    if not os.path.isdir(subFolder):
        os.makedirs(subFolder)
    shutil.copy(config_file, subFolder)         # copy oneview_config.json

    subFolder      = ymlFolder + 'servers/'
    if not os.path.isdir(subFolder):
        os.makedirs(subFolder)
    shutil.copy(config_file, subFolder)         # copy oneview_config.json

    subFolder      = ymlFolder + 'storage/'
    if not os.path.isdir(subFolder):
        os.makedirs(subFolder)
    shutil.copy(config_file, subFolder)         # copy oneview_config.json

    # Connect to new OneView instance to collect interconnect types information
    print(CR)
    print('#---------------- Connect to Oneview instance')

    # Oneview config

    with open(config_file) as json_data:
        config = json.load(json_data)
    oneview_client = OneViewClient(config)

    # load resource type
    api     = config["api_version"]
    print('X-API version used ---> {}'.format(config["api_version"]) )
    if api == '1200':
        rstype  = resource_type_ov5_00 
    if api == '1000':
        rstype  = resource_type_ov4_20 

    print(CR)
    print('#---------------- Query interconnect types ' )
    ov_interconnect_types = oneview_client.interconnect_types.get_all(sort='name:descending')

    #-------------- Generate playbooks
    allScriptCode           = []
    allScriptFile           = ymlFolder + 'all_playbooks.sh'
    sequence                = 1

    # OneView settings
    print(CR)
    print('#---------------- Generate playbooks for Oneview settings')

    ymlSubfolder        = ymlFolder + 'appliance/'
    if  not usersheet.empty:
        ymlFile             = ymlSubfolder + 'user.yml'
        generate_user_ansible_script(                   usersheet      ,  ymlFile)
    
        add_to_allScripts('Configure users ' , ymlFile)

    ymlSubfolder        = ymlFolder + 'settings/'
    if  not timelocalesheet.empty:
        ymlFile             = ymlSubfolder + 'timelocale.yml'
        generate_time_locale_ansible_script(                   timelocalesheet      ,  ymlFile)
    
        add_to_allScripts('Configure time locale ' , ymlFile)

    if not addresspoolsheet.empty:
        ymlFile             = ymlSubfolder + 'addresspool.yml' 
        generate_id_pools_ipv4_ranges_subnets_ansible_script(  addresspoolsheet     ,  ymlFile)

        add_to_allScripts('Configure address pool and subnet ' , ymlFile)
    
    if not snmpsheet.empty:
        ymlFile             = ymlSubfolder + 'snmpv1.yml'
        generate_snmp_v1_ansible_script(                       snmpsheet            ,  ymlFile)
        add_to_allScripts('Configure appliance snmp ' , ymlFile)

    print(CR)
    print('#---------------- Generate playbooks for Oneview resources')
    # OneView resources
    ymlSubfolder        = ymlFolder + 'appliance/'
    if not firmwaresheet.empty:
        ymlFile             = ymlSubfolder + 'firmwarebaseline.yml'        
        generate_firmware_bundle_ansible_script(firmwaresheet , ymlFile)

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure firmware baseline ' , ymlFile)
        sequence = sequence + 1   

    ymlSubfolder        = ymlFolder + 'settings/'
    if not scopesheet.empty:
        ymlFile             = ymlSubfolder + 'scope.yml'
        generate_scopes_ansible_script(scopesheet , ymlFile)

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure scope ' , ymlFile)
        sequence = sequence + 1 

    ymlSubfolder        = ymlFolder + 'networking/'
    if not ethernetnetworksheet.empty:
        ymlFile             = ymlSubfolder + 'ethernetnetwork.yml'
        generate_ethernet_networks_ansible_script(ethernetnetworksheet , ymlFile)

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure Ethernet network ' , ymlFile)
        sequence = sequence + 1 
    
    if not fcnetworksheet.empty:
        ymlFile             = ymlSubfolder + 'fcnetwork.yml'
        generate_fc_fcoe_networks_ansible_script(              fcnetworksheet ,              ymlFile)
        
        add_to_allScripts('Step {} - '.format(sequence) + 'Configure fc/fcoe network ' , ymlFile)
        sequence = sequence + 1 
    
    if not networksetsheet.empty:
        ymlFile             = ymlSubfolder + 'networkset.yml'
        generate_network_sets_ansible_script(                  networksetsheet,              ymlFile)

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure network set' , ymlFile)
        sequence = sequence + 1 
    
    if not ligsheet.empty:
        ymlFile             = ymlSubfolder + 'logicalinterconnectgroup.yml'
        generate_logical_interconnect_groups_ansible_script(   ligsheet , uplinksetsheet, ligsnmpsheet,  ymlFile )

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure logical interconnectgroup' , ymlFile)
        sequence = sequence + 1
    
    ymlSubfolder        = ymlFolder + 'storage/'
    if not sanmanagersheet.empty:
        ymlFile             = ymlSubfolder + 'sanmanager.yml'
        generate_san_manager_ansible_script(   sanmanagersheet ,  ymlFile )

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure SAN manager' , ymlFile)
        sequence = sequence + 1


    if not storagesystemsheet.empty:
        ymlFile             = ymlSubfolder + 'storagesystem.yml'
        generate_storage_system_ansible_script(   storagesystemsheet ,  ymlFile )

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure Storage System' , ymlFile)
        sequence = sequence + 1

    ymlSubfolder        = ymlFolder + 'servers/'
    if not enclosuregroupsheet.empty:
        ymlFile             = ymlSubfolder + 'enclosuregroup.yml'
        generate_enclosure_groups_ansible_script(              enclosuregroupsheet,          ymlFile)

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure enclosure group' , ymlFile)
        sequence = sequence + 1
    
    if not logicalenclosuresheet.empty:
        ymlFile             = ymlSubfolder + 'logicalenclosure.yml'
        generate_logical_enclosures_ansible_script(            logicalenclosuresheet,        ymlFile)

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure logical enclosure' , ymlFile)
        sequence = sequence + 1
    
    if not profiletemplatesheet.empty:
        ymlFile             = ymlSubfolder + 'profiletemplate.yml'
        generate_server_profile_templates_ansible_script(      profiletemplatesheet, profileconnectionsheet, profilelocalstoragesheet,  ymlFile)

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure profile template' , ymlFile)
        sequence = sequence + 1
    
    if not profilesheet.empty:
        ymlFile             = ymlSubfolder + 'profile.yml'
        generate_server_profiles_ansible_script(               profilesheet,         profileconnectionsheet, profilelocalstoragesheet,  ymlFile)

        add_to_allScripts('Step {} - '.format(sequence) + 'Configure profile' , ymlFile)
        sequence = sequence + 1
    
    #generate_inventory_file_ansible_script(                ymlFolder+'mac_wwnn.csv',    ymlFolder+'create_inventory_file.yml')
    generate_inventory_sp_ansible_script(                  profilesheet,            ymlFolder+'mac_wwnn.csv',        ymlFolder+'inventory.yml')

    write_to_file(allScriptCode, allScriptFile)

    print(CR)
    print('-----------')
    print('Execute this sh script {} to run all playbooks'.format(allScriptFile))
    print('-----------')
    print(CR)
