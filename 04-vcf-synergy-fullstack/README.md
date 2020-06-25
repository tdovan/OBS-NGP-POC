# 04-vcf-synergy-fullstack

The goal is to create a pipeline that automate the full provisionning process: provisionning the server in oneview and make it available in w VCF workload domain.

I'm currently finalizing a pipeline where I use concourse-ci + vault + ansible

![Concourse example](images/concourse-example.jpg)


## Concourse & Vault installation

### Concourse
```bash
ssh concourse.obs.hpecic.net
sudo yum update -y
dnf install git
dnf install jq
dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
dnf list docker-ce
dnf install docker-ce --nobest
systemctl start docker
systemctl enable docker
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

mkdir ~/concourse; cd ~/concourse
wget https://concourse-ci.org/docker-compose.yml
docker-compose up -d

Concourse will be running at http://concourse.obs.hpecic.net:8080/ (test/test)


wget https://github.com/concourse/concourse/releases/download/v6.3.0/fly-6.3.0-linux-amd64.tgz
tar -xvf fly-6.3.0-linux-amd64.tgz
mv fly /usr/local/bin/
chmod +x /usr/local/bin/fly
fly -t tutorial login -c http://concourse.obs.hpecic.net:8080/ -u test -p test

```

### Vault

```bash
# install vault dev
vault server -dev
export VAULT_ADDR='http://127.0.0.1:8200'
echo "jesbs1VojlxlSF84Qwq3UuZ5+hE8wdO4fyM2pLu+6pA=" > unseal.key
export VAULT_DEV_ROOT_TOKEN=s.gkj6aDD9bDGx26fipJ1u87iQ

Unseal Key: Vr66CgWJhWIU1Gm/eaz3Nf01ETc8dKeWgZYf6r+LB2g=
Root Token: s.gkj6aDD9bDGx26fipJ1u87iQ


vault status
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    1
Threshold       1
Version         1.4.2
Cluster Name    vault-cluster-608d3f78
Cluster ID      544a0801-1e44-169f-6a5e-7c5c5f047054
HA Enabled      false

# install secret
vault kv put secret/hello foo=world
vault kv put secret/hello foo=world excited=yes

vault kv get secret/hello
vault kv get -format=json secret/hello  | jq -r .data.data.excited

vault kv delete secret/hello

# secret engine
vault secrets enable -path=obs kv
vault secrets list
vault kv put obs/hello target=world
vault kv get obs/hello
vault kv put obs/my-secret value="s3c(eT"
vault kv get obs/my-secret
vault kv delete obs/my-secret
vault kv list obs/

# activate giihut
vault auth enable github

go to github and create an org: obs-hpe
https://github.com/orgs/obs-hpe/

vault write auth/github/config organization=obs-hpe
vault write auth/github/map/teams/ngp value=default,applications

github vault token: 6fd592c8a23b6443d313577af483e00d81132c2e

### hands-on tuto

```bash
git clone https://github.com/starkandwayne/concourse-tutorial.git
cd concourse-tutorial/tutorials/basic/task-hello-world

# task one-off
fly -t tutorial execute -c task_hello_world.yml
http://concourse.obs.hpecic.net:8080/builds/1

fly -t tutorial execute -c task_ubuntu_uname.yml
http://concourse.obs.hpecic.net:8080/builds/2

# pipeline
cd /root/github/concourse-tutorial/tutorials/basic/pipeline-resources
fly -t tutorial sp -c pipeline.yml -p hello-world
fly -t tutorial up -p hello-world

```