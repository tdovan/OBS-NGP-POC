# 00-Prepare your vm

## Install anaconda (python env) and other usefull stuff

```bash
sudo -i
ssh-keygen
ssh <IP-OF-YOUR-VM>
yum install tmux -y
yum install git

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

## Install oneview ansible module and sdk

```bash
mkdir -p /etc/hpe-ansible/
cd /etc/hpe-ansible/
pip install hpOneView
git clone https://github.com/HewlettPackard/oneview-ansible.git
cd /etc/hpe-ansible/oneview-ansible/
pip install -r requirements.txt
pip install jmespath
```

### Install Primera ansible module and sdk

```bash
pip install hpe3par-sdk
cd ~/workspace/github
git clone https://github.com/HewlettPackard/hpe3par_ansible_module

Add oneview and 3par/primera to the ansible.cfg
vi /etc/ansible/ansible.cfg
library         = /home/tdovan/workspace/github/oneview-ansible/library:/home/tdovan/workspace/github/hpe3par_ansible_module
module_utils    = /home/tdovan/workspace/github/oneview-ansible/library/module_utils:/root/anaconda3/envs/tf-3.6/lib/python3.6/site-packages:/root/anaconda3/lib/python3.7/site-packages

note: replace the path of the library and module_utils  with yours
```
