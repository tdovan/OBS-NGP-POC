# 00-Prepare your vm

## Install tmux, git, anaconda (python env) and other usefull stuff

```bash
sudo -i
ssh-keygen
ssh <IP-OF-YOUR-VM>
dnf install epel-release
dnf makecache
dnf install ansible

yum install git

yum install tmux -y
echo "set -g mouse on" > /root/.tmux.conf
tmux new -s obs
(crt+b + " for new pane)
(to attach the session afterwards: $ tmux attach -t obs)

cd /tmp/
curl -O https://repo.anaconda.com/archive/Anaconda3-5.3.1-Linux-x86_64.sh
bash Anaconda3-5.3.1-Linux-x86_64.sh

source ~/.bashrc
conda info
conda create --name python3.6 python=3.6
conda activate python3.6
```

## connect the cohesity share

```bash
mkdir /mnt/obs_share
mount -t nfs cohesity.obs.hpecic.net:/OBS_SHARE /mnt/obs_share
```

## Install oneview ansible module and sdk

```bash
mkdir -p /etc/ansible-hpe/
cd /etc/ansible-hpe/
pip install hpOneView
git clone https://github.com/HewlettPackard/oneview-ansible.git
cd /etc/ansible-hpe/oneview-ansible/
pip install -r requirements.txt
pip install jmespath
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

### validate Oneview and Primera ansible has been properly installed
all playbooks has been put in the cohesity repository

```bash
cd /mnt/obs_share/00-prepare-your-vm/
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

- in inventory/localhost: we set the ansible_python_interpreter as we are using conda env
```

next step, go to [02-deploy-server-with-osda](https://github.com/tdovan/OBS-NGP-POC/tree/master/02-deploy-server-with-osda)