# 00-Prepare your vm

## Install anaconda (python env)

```bash
ssh <IP-OF-YOUR-VM>
cd /tmp/
curl -O https://repo.anaconda.com/archive/Anaconda3-5.3.1-Linux-x86_64.sh
bash Anaconda3-5.3.1-Linux-x86_64.sh
source ~/.bashrc
conda info
pip install jmespath
conda create --name py3.6 python=3.6
conda activate py3.6
```

## Install oneview ansible module and sdk

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
