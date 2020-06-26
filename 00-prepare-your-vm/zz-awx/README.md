# awx tips

## awx tips

```bash
# add custom env path
curl -X PATCH 'http://obs:admin@localhost/api/v2/settings/system/'     -d '{"CUSTOM_VENV_PATHS": ["/opt/my-envs/"]}'  -H 'Content-Type:application/json'
sudo -i
dnf install epel-release
dnf makecache
dnf install ansible

# create venv
docker ps --format '{{ json .}}' | jq .
CONTAINER ID        IMAGE                 COMMAND                  CREATED             STATUS              PORTS                    NAMES
a201b96d6348        ansible/awx:13.0.0    "tini -- /usr/bin/la…"   15 hours ago        Up 15 hours         8052/tcp                 awx_task
dc2e3fa4c59f        ansible/awx:13.0.0    "tini -- /bin/sh -c …"   15 hours ago        Up 15 hours         0.0.0.0:80->8052/tcp     awx_web

--> connect to awx_web and awx_task
docker exec -it dc2e3fa4c59f bash
mkdir -p /opt/my-envs/
chmod 0755 /opt/my-envs/
sudo /usr/local/bin/virtualenv /opt/my-envs/oneview
sudo python3 -m venv /opt/my-envs/oneview
source /opt/my-envs/oneview/bin/activate
pip install hpOneView
yum install gcc
pip install psutil

sudo /opt/my-envs/oneview/bin/pip install hpOneView

/opt/my-envs/oneview/bin/pip freeze
. /opt/my-envs/oneview/bin/activate
sudo /var/lib/awx/venv/ansible/bin/pip freeze

vi /etc/ansible/ansible.cfg
library         = /etc/ansible-hpe/oneview-ansible/library:/etc/ansible-hpe/hpe3par_ansible_module
module_utils    = /etc/ansible-hpe/oneview-ansible/library/module_utils:/etc/ansible-hpe/hpe3par_ansible_module/Modules/:/opt/my-envs/oneview/lib/python3.6/site-packages/

alias ll='ls -lrt'
cd /var/lib/awx/projects/_8__obs_ngp_poc/00-prepare-your-vm/
vi oneview_version_facts.yml

# edit cred
vi /opt/my-envs/oneview/lib/python3.6/site-packages/hpOneView/oneview_client.py

# awx for default env
source /var/lib/awx/venv/ansible/bin/activate
pip install hpOneView
yum install gcc
pip install psutil


# patch job
curl -X PATCH 'http://obs:admin@localhost/api/v2/job_templates/13/' -d '{"custom_virtualenv": "/opt/my-envs/oneview/" }' -H 'Content-Type:application/json'



```