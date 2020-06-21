### OEM VMWARE Image - https://www.hpe.com/us/en/servers/hpe-esxi.html

---- Info on ESXi7 and CNA 3820/6820 drivers
https://my.vmware.com/web/vmware/details?downloadGroup=OEM-ESXI70-HPE&productId=974
CNA 6820 = HPE QLogic FastLinQ 10/25/50 GbE Drivers >> Marvell QL45604 > MRVL-E3-Ethernet-iSCSI-FCoE--1.0.0.0-1vmw.700.1.0.15843807
firmware 08.50.44 / vibs qedf version 1.3.41.0	
(https://www.vmware.com/resources/compatibility/detail.php?deviceCategory=io&productid=48976&releaseid=485&deviceCategory=io&details=1&keyword=6820&page=1&display_interval=10&sortColumn=Partner&sortOrder=Asc)
CNA 3820 = vibs https://www.vmware.com/resources/compatibility/search.php?deviceCategory=io&details=1&keyword=3820&page=1&display_interval=10&sortColumn=Partner&sortOrder=Asc
https://kb.vmware.com/s/article/78389
FCoE = qedf
esxcli software component apply -d /tmp/index.xml

Qlogic direct: http://driverdownloads.qlogic.com/QLogicDriverDownloads_UI/SearchByOs.aspx?ProductCategory=322&OsCategory=6&Os=167&OsCategoryName=VMware&ProductCategoryName=Converged+Network+Adapters&OSName=VMware+ESX%2FESXi
### VCF

#### FCoE
FCoE support in ESXi 7.0
https://kb.vmware.com/s/article/78389
It should also be noted that qedf driver that is supported ESXi 6.7 requires open FCoE. Since there is no open FCoE in 7.0, qedf driver will not function and must be replaced with the ESXi 7.0 async qedf driver.

CNA 6820 > Marvell QL45604 (https://support.hpe.com/hpesc/public/docDisplay?docLocale=en_US&docId=a00091476en_us)
CNA 3820 > QLogic BCM 57840S with integrated MAC/PHY > https://my.vmware.com/web/vmware/details?downloadGroup=DT-ESX70-MARVELL-QEDENTV-50189&productId=974


---- make HBA6820 works on ESXi7
ssh osda
scp /var/www/html/vibs/MRVL-E4-CNA-Driver-Bundle_5.0.189-1OEM.700.1.0.15525992_16014678-package.zip 10.15.61.111:/tmp/
ssh 10.15.61.111
cd /tmp
unzip MRVL-E4-CNA-Driver-Bundle_5.0.189-1OEM.700.1.0.15525992_16014678-package.zip
unzip MRVL-E4-CNA-Driver-Bundle_5.0.189-1OEM.700.1.0.15525992_16014678.zip
esxcli software component apply -d /tmp/index.xml

esxcfg-vmknic -l
esxcli network ip interface set -m 9000 -i vmk0
esxcli network ip interface list


esxcfg-nics -l
esxcfg-fcoe -l
for nic in `esxcli fcoe nic list | grep vmnic`
        do
        esxcli fcoe nic enable -n $nic
        esxcli fcoe nic discover -n $nic
        done
        esxcli fcoe adapter list
https://my.vmware.com/group/vmware/details?downloadGroup=DT-ESXI60-QLOGIC-QEDF-13360&productId=491&download=true&fileId=a82f9dda8d9f5ed1daa0cc13e8aaaab0&secureParam=792c6682f6fa6483a488a3f2cba180d0&uuId=83965e2c-e30f-4481-bf0f-101e03af1794&downloadType=

esxcli software vib install -v viburl
esxcli software vib install -v http://10.15.60.40/vibs/qedf-1.3.41.0-1OEM.600.0.0.2768847.x86_64.vib
index.xml

scp MRVL-E4-CNA-Driver-Bundle_5.0.189-1OEM.700.1.0.15525992_16014678-package.zip 10.15.61.110:/tmp/
unzip MRVL-E4-CNA-Driver-Bundle_5.0.189-1OEM.700.1.0.15525992_16014678-package.zip
unzip MRVL-E4-CNA-Driver-Bundle_5.0.189-1OEM.700.1.0.15525992_16014678.zip
esxcli software component apply -d /tmp/index.xml

---- create a new ESX7 iso with good CNA driver 
Create image
if using a proxy:
$webclient=New-Object System.Net.WebClient
$webclient.Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
[Net.ServicePointManager]::SecurityProtocol = "tls12"

$ pwsh
PowerShell ISE (runas administrator)
PS /root> Install-Module -Name VMware.PowerCLI –AllowClobber
Update-Module VMware.PowerCLI
Add-EsxSoftwareDepot -DepotUrl "C:\Users\tdovan\OneDrive - Hewlett Packard Enterprise\hpe\HPE_Accounts\_1_TA\Orange\_OBS\20200420_OBS RFP NGP\POC\vmware\VMware-ESXi-7.0.0-15843807-depot.zip"
Add-EsxSoftwareDepot -DepotUrl "C:\Users\tdovan\OneDrive - Hewlett Packard Enterprise\hpe\HPE_Accounts\_1_TA\Orange\_OBS\20200420_OBS RFP NGP\POC\vmware\MRVL-E4-CNA-Driver-Bundle_5.0.189-1OEM.700.1.0.15525992_16014678.zip"
New-EsxImageProfile -CloneProfile "ESXi-7.0.0-15843807-standard" -name "ESXi-7.0.0-15843807-standard-custom" -Vendor "HPE"

Get-EsxSoftwarePackage | Select-String -Pattern "qed"

Get-EsxSoftwarePackage -Name qedrntv -Vendor VMW | Remove-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
Get-EsxSoftwarePackage -Name qedentv -Vendor VMW | Remove-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"

Get-EsxSoftwarePackage -Name qedentv -Vendor QLC | Add-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
Get-EsxSoftwarePackage -Name qedf -Vendor QLC | Add-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
Get-EsxSoftwarePackage -Name qedi -Vendor QLC | Add-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
Get-EsxSoftwarePackage -Name qedrntv -Vendor QLC | Add-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"

Export-EsxImageProfile -ImageProfile "ESXi-7.0.0-15843807-standard-custom" -ExportToIso -FilePath "C:\Users\tdovan\OneDrive - Hewlett Packard Enterprise\hpe\HPE_Accounts\_1_TA\Orange\_OBS\20200420_OBS RFP NGP\POC\vmware\HPE-ESXi-7.0-custom.2.iso"
Export-EsxImageProfile -ImageProfile "ESXi-7.0.0-15843807-standard-custom" -ExportToBundle -FilePath "C:\Users\tdovan\OneDrive - Hewlett Packard Enterprise\hpe\HPE_Accounts\_1_TA\Orange\_OBS\20200420_OBS RFP NGP\POC\vmware\\HPE-ESXi-7.0-custom.2.zip"

-----
Get-EsxSoftwarePackage -Name qedentv -Vendor VMW | Remove-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
Get-EsxSoftwarePackage -Name qedf -Vendor VMW | Remove-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
Get-EsxSoftwarePackage -Name qedi -Vendor VMW | Remove-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
Get-EsxSoftwarePackage -Name qedrntv -Vendor VMW | Remove-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"

Get-EsxSoftwarePackage -Name qedentv -Vendor QLC | Add-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
Get-EsxSoftwarePackage -Name qedf -Vendor QLC | Add-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
Get-EsxSoftwarePackage -Name qedi -Vendor QLC | Add-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
Get-EsxSoftwarePackage -Name qedrntv -Vendor QLC | Add-EsxSoftwarePackage -ImageProfile "ESXi-7.0.0-15843807-standard-custom"
-----

Export-EsxImageProfile -ImageProfile "ESXi-7.0.0-15843807-standard-custom" -ExportToIso -FilePath "C:\Users\tdovan\OneDrive - Hewlett Packard Enterprise\hpe\HPE_Accounts\_1_TA\Orange\_OBS\20200420_OBS RFP NGP\POC\vmware\HPE-ESXi-7.0-custom.iso"
Export-EsxImageProfile -ImageProfile "ESXi-7.0.0-15843807-standard-custom" -ExportToBundle -FilePath "C:\Users\tdovan\OneDrive - Hewlett Packard Enterprise\hpe\HPE_Accounts\_1_TA\Orange\_OBS\20200420_OBS RFP NGP\POC\vmware\\HPE-ESXi-7.0-custom.zip"

Get-Module -Name VMware* -ListAvailable | Select Name,Version,ModuleBase


>>>> GOOD Driver Qlogic : https://my.vmware.com/group/vmware/details?downloadGroup=DT-ESX70-MARVELL-QEDENTV-50189&productId=974&download=true&fileId=e303fb88e2f295bf367c3c6983bb0cb7&secureParam=90100efdd4a5ed0e35ec7917aeb88cdf&uuId=19a3ab7c-a465-495f-b8d1-5b86fb1166e1&downloadType=


find the esxi boot disk
ls -la /bootbank
vmkfstools -P /vmfs/volumes/10096f8b-d044b0e9-8697-0c6ccda4bf06
[root@osda-nolocalstorage:/tmp] vmkfstools -P /vmfs/volumes/10096f8b-d044b0e9-8697-0c6ccda4bf06
vfat-0.04 (Raw Major Version: 0) file system spanning 1 partitions.
File system label (if any): BOOTBANK2
Mode: private
Capacity 4293591040 (65515 file blocks * 65536), 4120444928 (62873 blocks) avail, max supported file size 0
Disk Block Size: 512/0/0
UUID: 10096f8b-d044b0e9-8697-0c6ccda4bf06
Partitions spanned (on "disks"):
        naa.600508b1001c7ba8871f691e550a30fc:6
Is Native Snapshot Capable: NO


#### BGP routing
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

#### cleanup the cloudbuilder
```bash
https://kb.vmware.com/s/article/75172
ssh cloud-builder
vi /data/pgdata/pg_hba.conf
uncomment the line
local   replication     all                                     trust

systemctl restart postgres
sudo psql -U postgres -d bringup -h /home/postgresql/
delete from execution;
delete from "Resource";
\q
```
### Synergy : efuse a blade

```bash
curl https://packages.microsoft.com/config/rhel/7/prod.repo |  sudo tee /etc/yum.repos.d/microsoft.repo
sudo yum makecache
sudo yum install powershell
pwsh
PS /root> Install-Module hponeview.500
PS /root> $az1=Connect-HPOVMgmt -Appliance 10.7.9.20 -UserName admin -Password obs@cicGVA1234!
PS /root> Get-HPOVServer -ApplianceConnection $az1 | Get-HPOVAlert -State active | Set-HPOVAlert -Cleared

PS /root> Get-HPOVEnclosure
$encl1 = Get-HPOVEnclosure -Name "CZ20040WV4-frame1"
Reset-HPOVEnclosureDevice -Component Device -DeviceID 10 -Enclosure $encl1 -EFuse
Reset-HPOVEnclosureDevice -Enclosure $enclosure -Component Device -DeviceID 1

PS /root> Get-HPOVEnclosure
$encl2 = Get-HPOVEnclosure -Name "CZ20040WYK-frame2"
Reset-HPOVEnclosureDevice -Component Device -DeviceID 6 -Enclosure $encl2 -EFuse
Reset-HPOVEnclosureDevice -Component Device -DeviceID 7 -Enclosure $encl2 -EFuse


curl -k -i -H "accept: application/json" -H "content-type: application/json" -d '{"userName":"admin","password":"obs@cicGVA1234!"}' -X POST https://synergy.obs.hpecic.net/rest/login-sessions
curl -k -H "accept: application/json" -H "content-type: application/json" -H "auth: LTI3MTExODk0MTc5Ogwh9xtVHRPsskRskrZpG13qA2mmpGmV" -X GET https://synergy.obs.hpecic.net/rest/server-hardware -o server.xml

https://monpostit.fr/billet/serveur/incidents-serveur/efuse-reset-sur-une-lame-hpe-synergy/
```

## Detailed Step-by-Step

I have break down each steps:

- [00-deploy-hardware](00-deploy-hardware/README.md)
- [01-create-golden-image](01-create-golden-image/README.md)
- [02-create-oneview-server-template](02-create-oneview-server-template/README.md)
- [03-provision-bare-metal-server](03-provision-bare-metal-server/README.md)
- [04-deploy-kubespray](04-deploy-kubespray/README.md)
- [05-customize-kubernetes](05-customize-kubernetes/README.md)
  - Istio
  - Calico
  - Velero
