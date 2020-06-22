# 01-deploy-synergy-from-excel

convertto-ansibleplaybooks-from-excel.py is a python script that generates ansible playbooks to configure OneView resources and settings from an Excel file.
The Excel file provides OV setting values and OV resources values.
The script generates the following ansible playbooks:

   * addresspool.yml
   * firmwarebundle.yml
   * scope.yml
   * timelocale.yml
   * user.yml

   * ethernetnetwork.yml
   * fcnetwork.yml
   * networkset.yml
   * logicalinterconnectgroup.yml (with uplinkset)
   * enclosuregroup.yml
   * logicalenclosure.yml
   * profiletemplate.yml (with local storage and network connections)
   * profile.yml (with local storage and network connections)


    Note: The playbooks work with OneView 5.0

## Prerequisites
   * Virtual machine running Ubuntu 18.09
   * python 3.8
   * ansible 2.8
   * pandas library ( for reading/writing Excel files)
   * pip 
   * oneview-python SDK 5.0.0
   * oneview-ansible library 5.0.0

   * a running OV instance 5.0
   * SPP ISO file if you run playbook to upload firmware baseline



## Setup
In the Ubuntu machine, perform the following operations:

   1. sudo apt update
   2. sudo apt install software-properties-common
   3. sudo add-apt-repository ppa:deadsnakes/ppa
   #### install python3 and tools
   4. sudo apt install python3.8
   5. sudo apt install python3-setuptools
   6. sudo apt install python3-pip
   #### install pandas for Excel
   7. sudo pip3 install pandas
   8. sudo pip3 install xlrd

   9. sudo pip3 install requests
   10. sudo pip3 install ansible

   ### install OneView python SDK 5.0
   11. Install oneview python SDK
        *  git clone https://github.com/HewlettPackard/oneview-python.git 
        *  cd oneview-python
        *  pip3 install .
        * python setup.py install --user  

   ### install OneView Ansible SDK 5.0    
   12. Install oneview ansible library
        *  git clone https://github.com/HewlettPackard/oneview-ansible.git
	     *  cd oneview-ansible
        *  sudo pip3 install -r requirements.txt   
    

    
## Configuration
Create the following environment variables or create a login shell script to configure those environment variables 

   * export ANSIBLE_LIBRARY=/home-folder/oneview-ansible/library
   * export ANSIBLE_MODULE_UTILS=/home-folder/oneview-ansible/library/module_utils/


## OV configuration Excel file
Use the Synergy-Sample.xlsx as reference. In the Excel file, configure the following sheets:

   * Composer_OneView

        **ip**           --> IP address of the OneView instance      
        **userName**     --> administrator name  
        **password**     --> administrator password  
   
        **Note**:         The OneView instance needs to be online as the python script will connect to it to collect information 

   * User
   * TimeLocale
   * firmwareBundle
   * AddressPool
   * Scope
   * EthernetNetwork
   * FCNetwork
   * NetworkSet
   * LogicalInterconnectGroup
   * UplinkSet
   * EnclosureGroup
   * LogicalEnclosure
   * ProfileTemplate
   * Profile
   * ProfileConnection
   * ProfileLOCALStorage



## To generate ansible playbooks
On the Ubuntu machine, execute:
```
    python3 convertto-ansibleplaybooks-from-excel.py Synergy-Sample.xlsx

```
The script will create a hierarchy of folders that mirrors the OneView structure as seen in the GUI.
   * a subfolder **playbooks** from the current directory
   * **playbooks/appliance**    ---> YML files related to OV appliance configuration
   * **playbooks/settings**     ---> YML files related to OV settings
   * **playbooks/networking**   ---> YML files related to OV networking
   * **playbooks/servers**      ---> YML files related to OV servers settings

In addition, the script also generates:
   * a shell script **all_playbooks.sh** that will run all the playbooks in a sequential order
   * a YML file **inventory.yml** that collects WWWN, MAC, WWPN of each server profile



## To run ansible playbooks

   * all playbooks

```
    sh playbooks/all_playbooks.sh 

```

   * individual playbooks
   
```
    ansible-playbook playbooks/servers/profile.yml 
    ansible-playbook playbooks/settings/addresspool.yml 
```

## Notes:
   * Ensure that the **OV instance is up and running**. Otherwise the python script will fail to generate playbooks
   * The oneview_config.json contains information to connect to OV. Credential and IP address are configured from the sheet "composer" in the Excel file
   * The oneview_config.json file is created under playbooks and then copied to all subfolders: playbooks/appliance, playbooks/settings, playbooks/networking, playbooks/servers 
   * If you have a playbook to configure firmware baseline, the SPP ISO must be located under **playbooks/appliance**

## To learn ansible syntax for OneView playbooks
The Examples-Playbooks.zip provide all playbooks generated from the Excel sample file. Use those playbooks as examples of OneView playbooks

Enjoy!