# Tuto pour Pascal

```bash
# Installation de splunk
https://github.com/dennybritz/docker-splunk/tree/master/enterprise
http://awx.obs.hpecic.net:8000/en-US/app/launcher/home

# Create HTTP Event Collector (HEC)
TODO


# Sendind data to splunk + Configuring AWX to send to splunk
curl -k http://awx.obs.hpecic.net:8088/services/collector -H "Authorization:Splunk e54e310f-685c-45d5-a8c3-67a80d394bb3" \
  -d "{\"sourcetype\": \"obs\",\"event\":\"hello world\"}"

https://docs.ansible.com/ansible-tower/latest/html/administration/logging.html

# search in splunk
source="http:awx" (index="awx")
source="http:awx" (index="activity_stream")
source="http:awx" (index="job_events")
source="http:awx" (index="system_tracking")

source="http:awx" (index="awx")| spath playbook | search playbook="pascal/oneview_get_serverProfile.yml" |  rex "{\"log\":\"(?<jsonData>.*)"
|  eval _raw=replace(jsonData,"\\\\\"","\"")
|  spath

```

