# How TO

## Add vLCM cluster images for HPE
The components concerned are:
- iloamp: http://iloamp.obs.hpecic.net/
- vcenter: https://m01-vc01.vcf.obs.hpecic.net/

```bash
1. Install iloamp.The ova can be found at /mnt/obs_share/hpe/iLOAmplifierPack/iLOAmplifierPack_1.60_vmware.zip
2. In the iloamp Install the HSM plugin. Go to "Configuration and Setting" > "Add-on Service Manager" : install "HPE Hardware Support Manager (HSM) plug-in for VMware vLCM"
3. Register the vCenter in HSM: go to "HPE Hardware Support Manager (HSM) for VMware vLCM" and add the vCenter where you plan to have your vLCM cluster image managed
4. Import the SPP /mnt/obs_share/hpe/SPP/P26943_001_VUP10-SPP-VUP10.2020_0423.39.iso in the iloamp Baseline Management Firmware Baseline
5. Register the iloamp certificate in the vCenter.
ssh -l administrator@vsphere.local m01-vc01.vcf.obs.hpecic.net
Command> shell
true | openssl s_client -connect 10.15.60.50:443 -showcerts >/tmp/iloamp-cert.crt
/usr/lib/vmware-vmafd/bin/dir-cli trustedcert publish --cert /tmp/iloamp-cert.crt
Certificate pubished successfully
5. go to vCenter>HPE Hardware Support Manager (HSM) plug-in for VMware vLCM. you should see the SPP. Click on add "VMware ESXi 7.0 Upgrade Pack"
![HPE HSM SPP](iloamp-hsm-spp.jpg)
6. go to the vCenter cluster "ClusterForImage" and edit your image.
![HPE HSM SPP](iloamp-vLCM.jpg)

You're done
```
