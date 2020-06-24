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

## Display the ToR BGP routing for NSX-T AVN
The components concerned are:
- ToR-1: 10.15.65.254
- Tor-2: 10.15.66.254

In the Cloud Builder: vcf-ems-deployment-parameter-obs.xlsx/Deploy Parameters, AVN parameters:
![NSX-T AVN](nsx-avn.jpg)
These are the BGP networks craeted in the ToR 1 and 2

```bash
ssh 10.15.65.254
<epc_sw5950_b1r14_2>disp bgp routing ipv4

 Total number of routes: 17

 BGP local router ID is 2.2.2.2
 Status codes: * - valid, > - best, d - dampened, h - history
               s - suppressed, S - stale, i - internal, e - external
               a - additional-path
       Origin: i - IGP, e - EGP, ? - incomplete

     Network            NextHop         MED        LocPrf     PrefVal Path/Ogn

* >  2.2.2.2/32         127.0.0.1       0                     32768   ?
* >  10.6.57.0/24       10.6.57.20      0                     32768   ?
* >  10.6.57.20/32      127.0.0.1       0                     32768   ?
* >e 10.15.65.0/24      10.15.66.2      0                     0       65003?
*  e                    10.15.66.3      0                     0       65003?
* >  10.15.66.0/24      10.15.66.254    0                     32768   ?
*  e                    10.15.66.2      0                     0       65003?
*  e                    10.15.66.3      0                     0       65003?
* >  10.15.66.254/32    127.0.0.1       0                     32768   ?
* >  10.24.0.0/16       10.24.34.202    0                     32768   ?
* >  10.24.34.202/32    127.0.0.1       0                     32768   ?
* >e 100.64.176.0/31    10.15.66.2      0                     0       65003?
*  e                    10.15.66.3      0                     0       65003?
* >e 192.168.11.0       10.15.66.2      0                     0       65003?
*  e                    10.15.66.3      0                     0       65003?
* >e 192.168.31.0       10.15.66.2      0                     0       65003?
*  e                    10.15.66.3      0                     0       65003?

In the BGP routing table, you can see 4 networks:
1. 10.15.65.0/24 = UPLINK-1
2. 10.15.66.0/24 = UPLINK-2
3. 100.64.176.0/31 = peering network
4. 192.168.11.0 = xRegion network
5. 192.168.31.0 = Region A network

you're done