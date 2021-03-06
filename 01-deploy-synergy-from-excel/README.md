# 01-deploy-synergy-from-excel

convertto-ansibleplaybooks-from-excel.py is a python script that generates ansible playbooks to configure OneView resources and settings from an Excel file.
The Excel file provides OV setting values and OV resources values.
The script generates the following ansible playbooks:
1. addresspool.yml
1. firmwarebundle.yml
1. scope.yml
1. timelocale.yml
1. user.yml
1. ethernetnetwork.yml
1. fcnetwork.yml
1. networkset.yml
1. logicalinterconnectgroup.yml (with uplinkset)
1. enclosuregroup.yml
1. logicalenclosure.yml
1. profiletemplate.yml
1. profile.yml

## Quick start
Careful, thethis is supposed to configure a complete synergy appliance from scratch. For the POC, the synergy has already been configured. so this playbook cannot be executed.

### Generate the playbook

```bash
ssh root@10.15.60.206
conda activate python3.6
cd /mnt/obs_share/ansible/01-deploy-synergy-from-excel

python convertto-ansibleplaybooks-from-excel.py Synergy-Sample.xlsx

The script will create a hierarchy of folders that mirrors the OneView structure as seen in the GUI.
   * a subfolder **playbooks** from the current directory
   * **playbooks/appliance**    ---> YML files related to OV appliance configuration
   * **playbooks/settings**     ---> YML files related to OV settings
   * **playbooks/networking**   ---> YML files related to OV networking
   * **playbooks/servers**      ---> YML files related to OV servers settings

In addition, the script also generates:
   * a shell script **all_playbooks.sh** that will run all the playbooks in a sequential order
   * a YML file **inventory.yml** that collects WWWN, MAC, WWPN of each server profile
```

### Run the playbooks
```bash
To run ansible playbooks
   * all playbooks
    sh playbooks/all_playbooks.sh 

   * individual playbooks
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
(thanks to DungKHoang for his great work)


Next step, go to [02-deploy-server-with-osda](https://github.com/tdovan/OBS-NGP-POC/tree/master/02-deploy-server-with-osda)