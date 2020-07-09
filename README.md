# OBS NGP POC with HPE

This repository contains ready-to-use ansible playbooks and scripts to automate tasks.
The environnment already contains a VM ready-to-use. If you want a quick start, juts connect to it:

```bash
ssh admin@10.15.60.206
tmux attach -t obs
```

Otherwise, you can follow the instruction here: [00-prepare-your-vm](00-prepare-your-vm/README.md)

![ansible-playbooks-use-cases](images/ansible-playbook.jpg)

## Use cases

- [01-deploy-synergy-from-excel](01-deploy-synergy-from-excel/README.md)
Deploy Synergy fromwith input from a excel file. This playbooks can used to automate the deployment of a ne synergy. This is not applicable for the POC as the platform has already been configured.

- [02-deploy-server-with-osda](02-deploy-server-with-osda/README.md)
Deploy a server profile from a template + install the OS based on a kickstart.

- [03-deploy-vcf-node](03-deploy-vcf-node/README.md)
Deploy a server from a template + install the OS + commision the node in vcf + add the node to the VI Workload domain

![General workflow](images/general-workflow.png)

## Use cases for Pascal

In the following link, 2 uses cases are described: exporting a server profile to splunk and upgrading disk firmware
- [exportServerProfile and upgradeDiskFirmware](pascal/README.md)

## For curious people
I've added a bunch of playbook that can be leverage for your own use case :
[zz-ansible-playbooks](https://github.com/tdovan/OBS-NGP-POC/tree/master/zz-ansible-playbooks)

I've also added the tips/howto used to configure the platform [zz-howto](https://github.com/tdovan/OBS-NGP-POC/tree/master/zz-howto)

## API docs & Miscellanous

- [HPE Oneview API](https://techlibrary.hpe.com/docs/enterprise/servers/oneview5.2/cicf-api/en/index.html)
- [HPE Oneview PowerShell API](https://github.com/HewlettPackard/POSH-HPEOneView/)
- [HPE Oneview PowerShell Docs](https://hpe-docs.gitbook.io/posh-hpeoneview/cmdlets/v5.20)
- [HPE Oneview PowerShell Example](https://github.com/HewlettPackard/oneview-powershell-samples/)
- [HPE Oneview Ansible Module](https://github.com/HewlettPackard/oneview-ansible)
- [HPE Primera API](https://support.hpe.com/hpesc/public/docDisplay?docLocale=en_US&docId=emr_na-a00088912en_us)

- [VCF API](https://code.vmware.com/apis/921/vmware-cloud-foundation)
- [VCF PowerVCF examples](https://github.com/PowerVCF/PowerVCF/)
- [VCF PowerVCF Docs](https://github.com/PowerVCF/PowerVCF/)
- [VCF PowerCli](https://code.vmware.com/docs/11794/cmdlet-reference)
- [VCF API schema](https://vdc-download.vmware.com/vmwb-repository/dcr-public/906e5952-1237-4089-b618-a608b5efb1fc/47c2c76b-d71b-4fa0-bf17-57c292cd2395/index.html#_fcspec)


- [Cohesity API](https://developer.cohesity.com/apidocs-641.html#/rest)

