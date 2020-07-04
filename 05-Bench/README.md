# Solution Benchmark (Synergy + Primera + VCF + VSAN )
This part describe the bench methodology used to validate the end to end solution performance capabilities.

## Tools & Metrics

```bash
hcibench2.3.1/vdbench50407: write latency/read latency, IOPS
esxtop (u+f+e+j+k): monitoring of queues,  guest os, kernel, device (DQLEN, KAVG/cmd GAVG/cmd QAVG/cmd DAVG/rd KAVG/rd GAVG/rd QAVG/rd DAVG/wr KAVG/wr)
primera: monitoring of IOPS, read/write latency, IOPS via ssmc/cli
```

## Objectives
```bash
Understand and validate the metrics measured end-to-end.
Create a bench template that can be reproduce with predicatable results (read/write latecy and IOPS)
```

## Setup
```bash
1/ Install Synergy+Primera+WLD Primera and WLD VSAN (3 identical nodes each)

2/ Customize esx
2.1/ for Primera (FCoE) - this is done during the deployment of the ESXi7
# Remove previous 3PAR STP Rule
esxcli storage nmp satp rule remove -b -V "3PARdata" -M "VV" -s "VMW_SATP_ALUA" -P "VMW_PSP_MRU" -c "tpgs_on" -e ""

# 3PAR SATP Rule
esxcli system settings advanced set -o /Disk/QFullSampleSize -i 32
esxcli system settings advanced set -o /Disk/QFullThreshold -i 8
esxcli storage nmp satp set -P VMW_PSP_RR -s VMW_SATP_ALUA
esxcli storage nmp satp rule add -s "VMW_SATP_ALUA" -P "VMW_PSP_RR" -O "iops=1;policy=latency" -c "tpgs_on" -V "3PARdata" -M "VV" -e "HPE Primera Custom iSCSI/FC/FCoE ALUA Rule"

# check the config
esxcfg-scsidevs -m
esxcli storage core claimrule list


best practises:
- in oneview, create the connection FC/FCoE with the appropriate bandwith/QoS (16G/32G)
- create a single VMFS volume per LUN/vv (automated by oneview)
- for perf, define a single-initiator zoning on the FC switch (automated by oneview)
- present same LUN target id number to esxi host (automated by oneview)
- in Primera conf, separate the I/O loading over the available path the storage devices (automated by osda - SATP rules)

2.2/ Customize esx for VSAN (P416e Smart array connected to Synery D3920 disk module SAS/SATA)
TODO

3/ Deploy HCIBench and configure template


```
## Start the bench
```bash
go to HCIBench, select the template and run the bench
```

## monitor the bench
```bash
1/ hcibench: once the test started, you can connect to the grafana dashboard to see report in realtime. data are collected/stored by telegraf/influxdb. 
http://10.15.61.80:3000/d/vdbench/hcibench-vdbench-monitoring?orgId=1&from=1593730830000&to=1593745239000

2/ esx
vscsiStats -l > get the worldGroupID of the VM to monitor
vscsiStats -s -w $vmId > start the monitoring the vm
vscsiStats -x -w $vmId > stop the monitoring the vm
esxtop (u+f+e+j+k)

3/ Storage backend
3.1/ Primera
SSMC of CLI

3.1/ VSAN
esx CLI or HCIBench grafana



---
ressources:
esxtop: https://www.virten.net/vmware/esxtop/

Mastering VMware vSphere Storage: https://books.google.fr/books?id=0aFNCgAAQBAJ&pg=PA103&lpg=PA103&dq=DAVG/rd&source=bl&ots=4z8IM3Roow&sig=ACfU3U0XEYSF0zClHTBBVa7YTXlXOFKCTA&hl=fr&sa=X&ved=2ahUKEwi3x_W1v7DqAhUPExQKHZ6UBiMQ6AEwAHoECAoQAQ#v=onepage&q=DAVG%2Frd&f=false


Essential Virtual SAN (VSAN): Administrator's Guide to VMware Virtual SAN
https://books.google.fr/books?id=JDv_AwAAQBAJ&pg=PA18&lpg=PA18&dq=SATP+VSAN+SAS+DISK&source=bl&ots=VeXCy8voZr&sig=ACfU3U2DzlfZpX1aegSOyrM96edhsd6RPQ&hl=fr&sa=X&ved=2ahUKEwipyfXO0LDqAhXQSsAKHQG_BJAQ6AEwAHoECAoQAQ#v=onepage&q=SATP%20VSAN%20SAS%20DISK&f=false