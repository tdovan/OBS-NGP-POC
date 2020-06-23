# 02-deploy-server-with-osda

## Quick start

```bash
ssh root@10.15.60.206
conda activate python3.6
cd /mnt/obs_share/ansible/02-deploy-server-with-osda

vi inventory/host_vars/OSDA.yml
change the json input file for the nodes be created :
- to deploy 1 ESXI SY660 node: deploy_json_file: "data/deploy-1nodesSY660-primera-bfs.json"
- to deploy 4 VCF MGMT SY480 nodes : deploy_json_file: "data/deploy-vcf-mgmt-4nodes.json"
- to deploy 3 VCF VSAN SY480 nodes : deploy_json_file: "data/deploy-vcf-vsan-3nodes.json"
- to deploy 3 VCF Primera SY480 nodes : deploy_json_file: "data/deploy-vcf-primera-3nodes.json"
- to deploy the full VCF stack (12 nodes: mgmt+vsan+primera) : deploy_json_file: "data/deploy-vcf-fullstack-12nodes.json"

then run

ansible-playbook -i inventory/OSDA osda_deploy_server.yml
```