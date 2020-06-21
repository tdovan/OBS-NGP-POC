# OBS NGP POC with HPE

This repository contains the automation playbooks and scripts for :
- HPE Synergy OneView
- HPE OSDA (OS Deployment Automation)
- HPE Primera
- Cohesity
- VMWare Cloud Foundation

![General workflow](images/general-workflow.png)

## Prerequisites

Knowledge on ansible, linux, shell scripting
HPE Oneview API: https://techlibrary.hpe.com/docs/enterprise/servers/oneview5.2/cicf-api/en/index.html
HPE Primera API: https://support.hpe.com/hpesc/public/docDisplay?docLocale=en_US&docId=emr_na-a00088912en_us
Cohesity API: https://developer.cohesity.com/apidocs-641.html#/rest
VCF API: https://code.vmware.com/apis/921/vmware-cloud-foundation

Then, a linux jump station

## Quick Start

### Configure your jump station
cd /tmp/
curl -O https://repo.anaconda.com/archive/Anaconda3-5.3.1-Linux-x86_64.sh
bash Anaconda3-5.3.1-Linux-x86_64.sh
source ~/.bashrc
conda info
to update anaconda: conda update conda
to delete anaconda: rm -rf ~/anaconda3

pip install jmespath (to capture ip address of oneview server profile)
conda create --name k8s python=3.6
conda activate k8s

### Install oneview ansible module and sdk
```bash
mkdir -p ~/workspace/github
add oneview-sdk
pip install hpOneView
cd ~/workspace/github
git clone https://github.com/HewlettPackard/oneview-ansible.git
cd oneview-ansible
pip install -r requirements.txt
```

### Install Primera ansible module and sdk
```bash
add 3par-sdk
pip install hpe3par-sdk
cd ~/workspace/github
git clone https://github.com/HewlettPackard/hpe3par_ansible_module

Add oneview and 3par/primera to the ansible.cfg
vi /etc/ansible/ansible.cfg
library         = /home/tdovan/workspace/github/oneview-ansible/library:/home/tdovan/workspace/github/hpe3par_ansible_module
module_utils    = /home/tdovan/workspace/github/oneview-ansible/library/module_utils:/root/anaconda3/envs/tf-3.6/lib/python3.6/site-packages:/root/anaconda3/lib/python3.7/site-packages

note: replace the path of the library and module_utils  with yours
```

## Use cases


- [00-deploy-hardware](00-deploy-hardware/README.md)
- [01-create-golden-image](01-create-golden-image/README.md)
- [02-create-oneview-server-template](02-create-oneview-server-template/README.md)
- [03-provision-bare-metal-server](03-provision-bare-metal-server/README.md)
- [04-deploy-kubespray](04-deploy-kubespray/README.md)
- [05-customize-kubernetes](05-customize-kubernetes/README.md)
