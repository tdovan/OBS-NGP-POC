# 00-Prepare your vm

## Install tmux, git, anaconda (python env) and other usefull stuff

```bash
ssh <IP-OF-CENTOS8.1-VM>
sudo -i
dnf install epel-release
dnf makecache
dnf install ansible

yum install git

yum install tmux -y
echo "set -g mouse on" > /root/.tmux.conf
tmux new -s obs
(to attach the session afterwards: $ tmux attach -t obs)

cd /tmp/
curl -O https://repo.anaconda.com/archive/Anaconda3-5.3.1-Linux-x86_64.sh
bash Anaconda3-5.3.1-Linux-x86_64.sh

source ~/.bashrc
conda info
conda create --name python3.6 python=3.6
conda activate python3.6
```

## Connect the cohesity share where the playbooks are store

```bash
mkdir /mnt/obs_share
mount -t nfs cohesity.obs.hpecic.net:/OBS_SHARE /mnt/obs_share
```

## Installation of the modules

### pip module for the playbooks

```bash
pip install jmespath
pip install pandas
pip install xlrd
```

### Install oneview ansible module and sdk

```bash
mkdir -p /etc/ansible-hpe/
cd /etc/ansible-hpe/
pip install hpOneView
git clone https://github.com/HewlettPackard/oneview-ansible.git
cd /etc/ansible-hpe/oneview-ansible/
pip install -r requirements.txt
```

### Install Primera ansible module and sdk

```bash
pip install hpe3par-sdk
cd /etc/ansible-hpe/
git clone https://github.com/HewlettPackard/hpe3par_ansible_module

Add oneview and 3par/primera to the ansible.cfg
vi /etc/ansible/ansible.cfg
library         = /etc/ansible-hpe/oneview-ansible/library:/etc/ansible-hpe/hpe3par_ansible_module
module_utils    = /etc/ansible-hpe/oneview-ansible/library/module_utils:/etc/ansible-hpe/hpe3par_ansible_module/Modules/:/root/anaconda3/envs/python3.6/lib/python3.6/site-packages/
```

## Validation of the installation of ansible modules
All playbooks are stored in the cohesity repository /mnt/obs_share/

### 1st example: retrieve the API version available
```bash
cd /mnt/obs_share/ansible/00-prepare-your-vm/
ansible-playbook -i inventory/localhost oneview_version_facts.yml

note :
- the output of the playbook shows:
[localhost] => {
    "version": {
        "currentVersion": 1600,
        "minimumVersion": 120
    }
}
This means that we force the use of a specific oneview api version between 120 and 1600. This allows backward compatibility.
```

### 2nd example: retrieve information about server_profile_template

```bash
ansible-playbook -i inventory/localhost oneview_server_profile_template_facts.yml
```

### 3rd example: create a server profile template for VCF MGMT VSAN
```bash
ansible-playbook -i inventory/localhost oneview_create_serverProfileTemplate.yml
then, go to oneview to display the server profile create: https://synergy.obs.hpecic.net/#/profile-templates/show/
to delete the template:
ansible-playbook -i inventory/localhost oneview_delete_serverProfileTemplate.yml
```

### Other examples are available:

```bash
ll /etc/ansible-hpe/oneview-ansible/examples/
https://developer.hpe.com/
```

Next step, go to [01-deploy-synergy-from-excel](https://github.com/tdovan/OBS-NGP-POC/tree/master/01-deploy-synergy-from-excel)