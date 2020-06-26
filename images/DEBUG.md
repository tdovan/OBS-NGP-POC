### OEM VMWARE Image - https://www.hpe.com/us/en/servers/hpe-esxi.html

---- Info on ESXi7 and CNA 3820/6820 drivers
https://my.vmware.com/web/vmware/details?downloadGroup=OEM-ESXI70-HPE&productId=974


(https://www.vmware.com/resources/compatibility/detail.php?deviceCategory=io&productid=48976&releaseid=485&deviceCategory=io&details=1&keyword=6820&page=1&display_interval=10&sortColumn=Partner&sortOrder=Asc)
CNA 3820 = vibs https://www.vmware.com/resources/compatibility/search.php?deviceCategory=io&details=1&keyword=3820&page=1&display_interval=10&sortColumn=Partner&sortOrder=Asc
https://kb.vmware.com/s/article/78389


esxcli software component apply -d /tmp/index.xml


### VCF

#### FCoE
FCoE support in ESXi 7.0
https://kb.vmware.com/s/article/78389
It should also be noted that qedf driver that is supported ESXi 6.7 requires open FCoE. Since there is no open FCoE in 7.0, qedf driver will not function and must be replaced with the ESXi 7.0 async qedf driver.


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







