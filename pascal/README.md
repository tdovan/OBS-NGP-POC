# Tuto pour Pascal
Afin de mieux comprendre les principes d'automatisation avec ansible et AWX, nous allons décrire 2 cas d'usages


## Export d'une ServerProfile dans une base splunk

```bash
# Installation de splunk en docker
https://github.com/dennybritz/docker-splunk/tree/master/enterprise
http://splunk.obs.hpecic.net:8000/en-US/app/launcher/home

# Create HTTP Event Collector (HEC)
Se connecter à http://splunk.obs.hpecic.net:8000/en-US/app/launcher/home et suivre la procédure classique


# Test - Sendind data to splunk
curl -k http://awx.obs.hpecic.net:8088/services/collector -H "Authorization:Splunk e54e310f-685c-45d5-a8c3-67a80d394bb3" \
  -d "{\"sourcetype\": \"obs\",\"event\":\"hello world\"}"

# Configuring AWX to send data to splunk
https://docs.ansible.com/ansible-tower/latest/html/administration/logging.html
Once configure, every job execution will be logged in splunk

# Search in splunk
Go to : http://splunk.obs.hpecic.net:8000/en-US/app/launcher/home
here some example of search pattern
source="http:awx" (index="awx")
source="http:awx" (index="activity_stream")
source="http:awx" (index="job_events")
source="http:awx" (index="system_tracking")

source="http:awx" (index="awx")| spath playbook | search playbook="pascal/oneview_get_serverProfile.yml" |  rex "{\"log\":\"(?<jsonData>.*)"
|  eval _raw=replace(jsonData,"\\\\\"","\"")
|  spath

```


## Disk Firmware upgrade automation

```bash
The first action is to gather_facts about configuration on the Synergy system:
- Smart Array type : integrated or physical (HPE Smart Array P416ie-m SR G10)
- Transport type: SAS or SATA
- Media type: HDD/SSD/NVMe
- Size : 480G, 1.6T..
- Model type: MK000480GWXFF or MK001920GWSSE
- Firmware version
- Form factor: SFF

In our case, we are using the P416ie in Mezz1 attached to :
- 2x local disk of 480GB/SSD/SATA/MK000480GWXFF/HPG0/Mixed Used: use for OS ESXi install with RAID1
- 2x D3940 (Frame1, bay 11 and Frame2, bay 11) with 40 disk 1920GB/SSD/SATA/MK001920GWSSE/HPG1 : use for VSAN JBOD
- 1x D3940 (Frame1, bay 9) with 34 disks SAS: use for VSAN JBOD
  - 24x 1.6TB model MO001600JWDLA (mixed used): : HPD2 / https://support.hpe.com/hpsc/swd/public/detail?swItemId=MTX_8a61af0f6c8041ff91ecd4ada8
  - 4 x 400G  model EO000400JWDKP (write intensive): HPD2 / https://support.hpe.com/hpsc/swd/public/detail?swItemId=MTX_8a61af0f6c8041ff91ecd4ada8
  - 4 x 300G  model EG0300JFCKA: HPD6(D)(20 Dec 2019) / https://support.hpe.com/hpsc/swd/public/detail?swItemId=MTX_886fc4239a1e44af8bcd5fe3d6#tab-history

note: Online firmware flashing of drives attached to an HPE Smart Array controller running in Zero Memory (ZM) mode or an HPE ProLiant host bus adapter (HBA) is NOT supported. Only offline firmware flashing of drives is supported for these configurations.


```