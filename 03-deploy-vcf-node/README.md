# 03-deploy-vcf-node

## 1-REST API for validating new host before commissioning
Validate if the host is ready for commissioning.

```bash
curl -k  'https://sddc01.vcf.obs.hpecic.net/v1/hosts/validations/commissions' -i -u 'admin:PASSWORD' -X POST \
    -H 'Content-Type: application/json' \
    -d '[ {
  "fqdn" : "vcfwlkd06.vcf.local",
  "username" : "root",
  "password" : "PASSWORD",
  "storageType" : "VSAN",
  "networkPoolId" : "17a60a94-dc22-422b-a296-be7d614b74cc",
  "networkPoolName" : "pod-wlkdnetworkpool"
}]'

[output]
HTTP/1.1 202
Server: nginx/1.15.3
Date: Thu, 29 Aug 2019 08:13:38 GMT
Content-Type: application/json;charset=UTF-8
Transfer-Encoding: chunked
Connection: keep-alive
Location: /v1/hosts/validations/32ad835f-748e-4ed6-b0b9-163c03eab160
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Frame-Options: DENY

{"id":"32ad835f-748e-4ed6-b0b9-163c03eab160","description":"Validate input specification to commission one or more hosts to VMware Cloud Foundation","executionStatus":"IN_PROGRESS","validationChecks":[{"description":"Validating input specification","resultStatus":"UNKNOWN"},{"description":"Validating host vcfwlkd06.vcf.local","resultStatus":"UNKNOWN"}]}
```

#2-REST API to poll for hosts validation status

The validation may take longer time than the REST call so wait till the validation is complete by polling for the status using the following command:

```bash
curl -k -XGET "https://sddc01.vcf.obs.hpecic.net/v1/hosts/validations/32ad835f-748e-4ed6-b0b9-163c03eab160" -i -u 'admin:PASSWORD' -H 'Content-Type: application/json'

[output]
HTTP/1.1 200
Server: nginx/1.15.3
Date: Thu, 29 Aug 2019 08:44:14 GMT
Content-Type: application/json;charset=UTF-8
Transfer-Encoding: chunked
Connection: keep-alive
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Frame-Options: DENY
Strict-Transport-Security: max-age=15768000

{"id":"32ad835f-748e-4ed6-b0b9-163c03eab160","description":"Validate input specification to commission one or more hosts to VMware Cloud Foundation","executionStatus":"COMPLETED","resultStatus":"SUCCEEDED","validationChecks":[{"description":"Validating input specification","resultStatus":"SUCCEEDED"}]}
```

#3-REST API to commission new host
Finally commission the host if there are no errors in the validation
curl -k  'https://sddc01.vcf.obs.hpecic.net/v1/hosts' -i -u 'admin:PASSWORD' -X POST -H 'Content-Type: application/json'  -d '[ {
  "fqdn" : "vcfwlkd06.vcf.local",
  "username" : "root",
  "password" : "PASSWORD",
  "storageType" : "VSAN",
  "networkPoolId" : "17a60a94-dc22-422b-a296-be7d614b74cc",
  "networkPoolName" : "pod-wlkdnetworkpool"
}]'

[output]
HTTP/1.1 202
Server: nginx/1.15.3
Date: Thu, 29 Aug 2019 08:26:54 GMT
Content-Type: application/json;charset=UTF-8
Transfer-Encoding: chunked
Connection: keep-alive
Location: /v1/tasks/fa196af9-8390-4f85-b43a-24aeb5ea4b6c
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Frame-Options: DENY

{"id":"fa196af9-8390-4f85-b43a-24aeb5ea4b6c","status":"IN_PROGRESS"}

Capture the ‘id’ of the task from the output for checking the task status.

#4-REST API to Poll for task status for completion
The REST call for commissioning the host may take longer time so wait until the commissioning task is completed by polling for task status using the following REST call:
curl -k -XGET "https://sddc01.vcf.obs.hpecic.net/v1/tasks/fa196af9-8390-4f85-b43a-24aeb5ea4b6c" -i -u 'admin:PASSWORD' -H 'Content-Type: application/json'

[output]
HTTP/1.1 200
Server: nginx/1.15.3
Date: Thu, 29 Aug 2019 08:35:24 GMT
Content-Type: application/json;charset=UTF-8
Transfer-Encoding: chunked
Connection: keep-alive
Set-Cookie: JSESSIONID=7676436DE11482839B0AEAF89558EA9B; Path=/; HttpOnly
X-Application-Context: application:prod:7100
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Frame-Options: DENY
Strict-Transport-Security: max-age=15768000

{"id":"fa196af9-8390-4f85-b43a-24aeb5ea4b6c","name":"Commissioning host(s) vcfwlkd06.vcf.local to VMware Cloud Foundation","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.352Z","subTasks":[{"name":"ValidateHostsAction","description":"Validate Hosts before commissioning","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.338Z","errors":[]},{"name":"AcquireLockContractAction","description":"Acquire lock","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.339Z","errors":[]},{"name":"SaveToInventoryAction","description":"Saves given hosts into inventory and associate them with given network pool.","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.340Z","errors":[]},{"name":"UpdateTaskRegistrationAction","description":"Updates task-registration with the resources(UUIDs).","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.341Z","errors":[]},{"name":"HostVibValidationAction","description":"Validate the hosts for any disallowed VIBS","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.342Z","errors":[]},{"name":"HostMaintenanceModeValidationAction","description":"Verifies that none of the hosts are in maintenance mode.","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.342Z","errors":[]},{"name":"FetchDnsAndNtpAction","description":"Fetches DNS \u0026 NTP IPs","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.344Z","errors":[]},{"name":"FetchNfsMountsAction","description":"Fetches NFS Mounts.","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.345Z","errors":[]},{"name":"ConfigureDnsAction","description":"Configures DNS Server IPs on given hosts.","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.346Z","errors":[]},{"name":"ConfigureNtpAction","description":"Configures NTP Server IPs on given hosts.","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.347Z","errors":[]},{"name":"FetchHostsAttributesAction","description":"Fetches all the attributes (including esxi version) for the given hosts.","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.348Z","errors":[]},{"name":"RotateHostSshKeysAction","description":"Rotates SSH Keys for the given hosts.","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.349Z","errors":[]},{"name":"CreateNfsDatastoreAction","description":"Configures NFS Datastore on the given hosts.","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.350Z","errors":[]},{"name":"UpdateKnownHostsOnSddcManagerAction","description":"Updates sddcmanager known_hosts with given hosts ssh keys","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.351Z","errors":[]},{"name":"UpdateInventoryAction","description":"Updates logical inventory with the given hosts","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.351Z","errors":[]},{"name":"ReleaseLockContractAction","description":"Release lock","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T08:26:54.351Z","errors":[]}],"errors":[],"resources":[{"resourceId":"3066c035-c6cc-459d-82ed-8d09bc8bd57d","type":"Esxi"}]}

Poll until ‘status’ is set to SUCCESSFUL.


#4-REST API for expanding existing cluster
Add commissioned host to an existing VCenter cluster to expand the capacity

REST API for getting the clusters

Use the following REST call for querying the available VCenter clusters.

curl -k -XGET "https://sddc01.vcf.obs.hpecic.net/v1/clusters" -i -u 'admin:PASSWORD' -H 'Content-Type: application/json'

The output is like:
HTTP/1.1 200
Server: nginx/1.15.3
Date: Thu, 29 Aug 2019 09:04:29 GMT
Content-Type: application/json;charset=UTF-8
Transfer-Encoding: chunked
Connection: keep-alive
X-Application-Context: application:prod:7200
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Frame-Options: DENY
Strict-Transport-Security: max-age=15768000

{"elements":[{"id":"1948d141-2d8e-4069-a73f-e37fa96778ce","name":"pod-m01-mgmt01","hosts":[{"id":"f712bd96-cece-40f8-8fb1-7c03a0c09e9b"},{"id":"64693796-7402-41b9-b272-186b3baa198d"},{"id":"e7542c61-f142-4430-bf34-f429d6dccc40"},{"id":"81511ed2-db8e-44df-b170-ee48f71865d3"}]},{"id":"2996b07d-8143-4f06-ab49-028432d039cf","name":"wlkd-domain1","hosts":[{"id":"983559f9-5ef4-4947-904b-ca6e5926ea2b"},{"id":"616595d0-47d7-472e-a7c2-1aa30f250b1e"},{"id":"64724401-225e-431c-81de-42640717cd23"}]}]}
The above result contains 2 clusters details in JSON format.
From the output JSON, capture the ‘id’ for the cluster wlkd-domain1 ( "2996b07d-8143-4f06-ab49-028432d039cf" ).


Get UNASSIGNED_USEABLE Hosts
For expanding the VCenter cluster with new hypervisor hosts, get the unassigned commissioned hosts from SDDC manager using the following call:
curl -k -XGET "https://sddc01.vcf.obs.hpecic.net/v1/hosts?status=UNASSIGNED_USEABLE" -i -u 'admin:PASSWORD' -H 'Content-Type: application/json'

The output is like:
HTTP/1.1 200
Server: nginx/1.15.3
Date: Thu, 29 Aug 2019 09:35:06 GMT
Content-Type: application/json;charset=UTF-8
Transfer-Encoding: chunked
Connection: keep-alive
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Frame-Options: DENY
Strict-Transport-Security: max-age=15768000

{"elements":[{"id":"3066c035-c6cc-459d-82ed-8d09bc8bd57d","esxiVersion":"6.7.0-13006603","fqdn":"vcfwlkd06.vcf.local","hardwareVendor":"HPE","hardwareModel":"Synergy 480 Gen10","ipAddresses":[{"ipAddress":"10.10.108.189","type":"MANAGEMENT"}],"cpu":{"frequencyMHz":62253.7421875,"cores":24,"cpuCores":[{"frequencyMHz":2593.90625,"model":"intel","manufacturer":"Intel(R) Xeon(R) Gold 6126 CPU @ 2.60GHz"},{"frequencyMHz":2593.906005859375,"model":"intel","manufacturer":"Intel(R) Xeon(R) Gold 6126 CPU @ 2.60GHz"}]},"memory":{"totalCapacityMB":261789.125},"storage":{"totalCapacityMB":0.0,"disks":[{"capacityMB":763097.8125,"diskType":"FLASH"},{"capacityMB":763097.8125,"diskType":"FLASH"},{"capacityMB":763097.8125,"diskType":"FLASH"},{"capacityMB":381554.09375,"diskType":"FLASH"}]},"physicalNics":[{"deviceName":"vmnic0","macAddress":"b6:45:eb:80:0c:1b"},{"deviceName":"vmnic1","macAddress":"b6:45:eb:80:0c:1c"}],"status":"UNASSIGNED_USEABLE"}]}[root@localhost ~]#

Get the ‘id’ for the available host(s) from the above response. This will be used for REST call for expanding the cluster.



Validate the host for expand the cluster ‘wlkd-domain1’
Provide available ‘id’ of unassigned host to this REST API to validate for cluster compatibility. Here is the validation call:
curl -k -XPOST "https://sddc01.vcf.obs.hpecic.net/v1/clusters/2996b07d-8143-4f06-ab49-028432d039cf/validations/updates" -i -u 'admin:PASSWORD' -H 'Content-Type: application/json' -d '{
  "clusterExpansionSpec" : {
    "hostSpecs" : [ {
      "id" : "3066c035-c6cc-459d-82ed-8d09bc8bd57d"
    } ]
  }
}'

The output is like:
HTTP/1.1 200
Server: nginx/1.15.3
Date: Thu, 29 Aug 2019 09:39:07 GMT
Content-Type: application/json
Transfer-Encoding: chunked
Connection: keep-alive
X-Application-Context: application:prod:7200
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Frame-Options: DENY
Strict-Transport-Security: max-age=15768000

{"id":"65e2c45b-489f-4840-a8e3-42fcd59d92a3","description":"Validating Cluster Expansion Spec","executionStatus":"COMPLETED","resultStatus":"SUCCEEDED","validationChecks":[{"description":"ClusterExpansionSpecValidation","resultStatus":"SUCCEEDED"}]}

If the ‘resultStatus’ is SUCCEEDED proceed expanding the cluster.

Expand the cluster
If validation passes then add the host to the cluster to perform the cluster expand operation using the following call:
curl -k -XPATCH "https://sddc01.vcf.obs.hpecic.net/v1/clusters/2996b07d-8143-4f06-ab49-028432d039cf" -i -u 'admin:PASSWORD' -H 'Content-Type: application/json' -d '{      "clusterExpansionSpec" : {
    "hostSpecs" : [ {
      "id" : "3066c035-c6cc-459d-82ed-8d09bc8bd57d"
    } ]
  }
}'

The output is like:
HTTP/1.1 202
Server: nginx/1.15.3
Date: Thu, 29 Aug 2019 09:43:42 GMT
Content-Type: application/json
Transfer-Encoding: chunked
Connection: keep-alive
X-Application-Context: application:prod:7200
Location: /v1/tasks/dc8101b6-4ae3-4467-a084-7e0bf79664de
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Frame-Options: DENY

{"id":"dc8101b6-4ae3-4467-a084-7e0bf79664de","name":"Adding new host(s) to cluster","status":"IN_PROGRESS","creationTimestamp":"2019-08-29T09:43:41.989Z"}[root@localhost ~]#


Poll for status of expand cluster task
curl -k -XGET "https://sddc01.vcf.obs.hpecic.net/v1/tasks/dc8101b6-4ae3-4467-a084-7e0bf79664de" -i -u 'admin:PASSWORD' -H 'Content-Type: application/json'

The output is like: 
HTTP/1.1 200
Server: nginx/1.15.3
Date: Thu, 29 Aug 2019 09:45:41 GMT
Content-Type: application/json;charset=UTF-8
Transfer-Encoding: chunked
Connection: keep-alive
Set-Cookie: JSESSIONID=901E835E4356820E087EC55BBBCDBA19; Path=/; HttpOnly
X-Application-Context: application:prod:7100
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Frame-Options: DENY
Strict-Transport-Security: max-age=15768000

{"id":"dc8101b6-4ae3-4467-a084-7e0bf79664de","name":"Adding new host(s) to cluster","status":"IN_PROGRESS","creationTimestamp":"2019-08-29T09:43:42.161Z","subTasks":[{"name":"Validate Host Spec Action","description":"Validate ESXi Host Input Specification","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T09:43:42.133Z","errors":[]},{"name":"Acquire Lock Action","description":"Acquire Lock for ESXi Host Addition","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T09:43:42.134Z","errors":[]},{"name":"Esxis Host Ip Allocation Action","description":"Allocate ESXi Host IP Addresses","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T09:43:42.135Z","errors":[]},{"name":"Fetch Add Host Licenses Action","description":"Fetch the esxi license from the spec or retrieve from LM","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T09:43:42.136Z","errors":[]},{"name":"Add Host Update Logical Inventory Action","description":"Update ESXi Host Data in Inventory","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T09:43:42.138Z","errors":[]},{"name":"RegisterTaskAction","description":"Register Current Task","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T09:43:42.138Z","errors":[]},{"name":"Generate Add Host Internal Model Action","description":"Generate Internal Model for ESXi Host Addition","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T09:43:42.138Z","errors":[]},{"name":"Validate Add Host Internal Model Action","description":"Validate Internal Model for ESXi Host Addition","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T09:43:42.139Z","errors":[]},{"name":"Prepare Add Host Input Action","description":"Create input map for add host operation","status":"SUCCESSFUL","creationTimestamp":"2019-08-29T09:43:42.140Z","errors":[]},{"name":"ValidateHostVmotionConnectivityAction","description":"Validate Vmotion network connectivity","status":"IN_PROGRESS","creationTimestamp":"2019-08-29T09:43:42.141Z","errors":[]},{"name":"PrepareEsxiAction","description":"Prepare ESXi Host","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.142Z","errors":[]},{"name":"FetchClusterMoidAction","description":"Get vSphere Cluster MOID","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.143Z","errors":[]},{"name":"AddHostsToDatacenterAction","description":"Add ESXi Hosts to Data Center","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.144Z","errors":[]},{"name":"EnterHostsInMaintenanceModeAction","description":"Enter Maintenance Mode on ESXi Hosts","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.145Z","errors":[]},{"name":"AddHostsToDvsAction","description":"Add ESXi Hosts to vSphere Distributed Switch","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.146Z","errors":[]},{"name":"CreateVmotionVmknicsAction","description":"Create vMotion vmknic(s) on ESXi Host","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.147Z","errors":[]},{"name":"CreateVsanVmknicsAction","description":"Create vSAN vmknic(s) on ESXi Host","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.148Z","errors":[]},{"name":"MigrateHostManagementVmknicsToDvsAction","description":"Migrate ESXi Host Management vmknic(s) to vSphere Distributed Switch","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.151Z","errors":[]},{"name":"DetachVmnicsFromVswitchAction","description":"Detach vmknic(s) from vSphere Standard Switch","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.151Z","errors":[]},{"name":"AttachVmnicsToDvsAction","description":"Attach vmknic(s) to vSphere Distributed Switch","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.151Z","errors":[]},{"name":"RemoveHostVswitchAction","description":"Remove vSphere Standard Switches from ESXi Hosts","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.151Z","errors":[]},{"name":"AddHostsToClusterAction","description":"Add ESXi Hosts to vSphere Cluster","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.153Z","errors":[]},{"name":"ConfigurePowerManagementPolicyOnHostWithEsxAction","description":"Configure Power Management Policy on ESXi Host","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.154Z","errors":[]},{"name":"VsanClaimDisksAction","description":"Create vSAN Disk Groups","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.155Z","errors":[]},{"name":"ClearAlarmsOnHostsAction","description":"Clear Alarms on ESXi Hosts","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.156Z","errors":[]},{"name":"ResolveNsxHostPrepIssuesAction","description":"Resolve ESXi Host Preparation Issues for NSX","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.157Z","errors":[]},{"name":"ExitHostsFromMaintenanceModeAction","description":"Exit Maintenance Mode on ESXi Hosts","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.158Z","errors":[]},{"name":"Add Host Update Status In Logical Inventory Action","description":"Update ESXi Host Data in Inventory","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.159Z","errors":[]},{"name":"Release Lock Action","description":"Release Lock for ESXi Host Addition","status":"PENDING","creationTimestamp":"2019-08-29T09:43:42.160Z","errors":[]}],"errors":[],"resources":[{"resourceId":"2996b07d-8143-4f06-ab49-028432d039cf","type":"Cluster"},{"resourceId":"f04bb06b-3e6d-4faa-8d9b-87ba567c0f60","type":"Domain"},{"resourceId":"3066c035-c6cc-459d-82ed-8d09bc8bd57d","type":"Esxi"}]}

If ‘status’ is SUCCESSFUL then the host must appear in VCenter like this:
![results](images/add-vcf-node-results.png)




Next step, go to [04-vcf-synergy-fullstack](https://github.com/tdovan/OBS-NGP-POC/tree/master/04-vcf-synergy-fullstack)