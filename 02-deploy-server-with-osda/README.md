# 02-deploy-server-with-osda

OSDA stands for Operating System Deployment Automation. It allows :
1. to create a physical server (OV server profile from template). Current  support: Gen9/Gen10, iLO 5 and Synergy.
1. install the OS. Current support: ESXi6.x, 7.x, CentOS/RHEL 7.x and 8.x.

It is developed by HPE and and free of charge.

## Quick start

### Choose the server to deploy
```bash
ssh root@10.15.60.206
conda activate python3.6
cd /mnt/obs_share/ansible/02-deploy-server-with-osda

### to deploy 1 ESXI SY660 node:
change the json input file for the nodes be created :
vi inventory/host_vars/OSDA.yml
"data/deploy-1nodesSY660-primera-bfs.json"

### to deploy 4 VCF MGMT SY480 nodes:
deploy_json_file: "data/deploy-vcf-mgmt-4nodes.json"

### to deploy 3 VCF VSAN SY480 nodes:
data/deploy-vcf-vsan-3nodes.json

### to deploy 3 VCF Primera SY480 nodes
deploy_json_file: "data/deploy-vcf-primera-3nodes.json"

### to deploy the full VCF stack (12 nodes: mgmt+vsan+primera
deploy_json_file: "data/deploy-vcf-fullstack-12nodes.json"
```

### Deploy the servers
```bash
ansible-playbook -i inventory/OSDA osda_deploy_server.yml
```

Next step, go to [03-deploy-vcf-node](https://github.com/tdovan/OBS-NGP-POC/tree/master/03-deploy-vcf-node)