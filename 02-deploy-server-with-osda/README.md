# OSDA playbooks
Playbooks to manage and deploy OSDA

## Pre-requisites
In order to successfully utilize these OSDA playbooks, the following pre-requisites should be met.

- OSDA service should be UP and RUNNING
- Firewall should allow connectivity between ansible server and OSDA server

# Usage

## Introduction
This playbooks will validate the input parameters, check the OSDA connectivity, provisions OS using the OSDA rest api, verifies the REST tasks and validates if all the server OS IP addresses are reachable.

The playbooks is successful passed only when all the OS deployments are successful.

## Inputs

The inputs of this playbook should be defined in two places.

1. The playbooks relies on the ansible host vars to fetch the  details of OSDA server, port and extra options needed for the deployment. And it is present in the path ```inventory/host_vars/OSDA.yml```. These inputs has be modified by running playbooks

2. The json file that is required by the OSDA to deploy operating system be completely filled and should be updated in the path ```data/deploy.json```. This file is used during the deployment

## Execute

Once the input files are configured, the playbook can be triggered using the following command:

```ansible-playbook -i inventory/OSDA osda_deploy_server.yml```

# TODO
1. Instead of using filled json file, use the inputs from end user and populate json
2. Validate the OS images are already present
3. Using REST API tasks to validate if the OS deployment is successful
