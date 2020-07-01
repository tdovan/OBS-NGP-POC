# Tuto pour Pascal

```bash
# Installation de splunk
https://github.com/dennybritz/docker-splunk/tree/master/enterprise
http://awx.obs.hpecic.net:8000/en-US/app/launcher/home

# Create HTTP Event Collector (HEC)


#send data to splunk
curl -k http://awx.obs.hpecic.net:8088/services/collector -H "Authorization:Splunk e54e310f-685c-45d5-a8c3-67a80d394bb3" \
  -d "{\"sourcetype\": \"obs\",\"event\":\"hello world\"}"

# search in splunk
source="http:awx" (index="awx")
source="http:awx" (index="activity_stream")
source="http:awx" (index="job_events")
source="http:awx" (index="system_tracking")

```

