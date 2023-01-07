# kafka-connect-task-monitor-slack-alert

Source credit - https://gist.github.com/rueedlinger/76af36d04a0798a8e1f43ed16595bd97

Simple python job to monitor the kafka connect tasks status using kafka connect API.

Deploy as background process or add in cron job

`nohup python3 kconnect_alert.py > output.log 2>&1  & `

#### cronjob
`*/5 * * * * python3 kconnect_alert.py 2>&1 >> connect_monitor.log`

<img width="757" alt="slack-Kafka-alert-template" src="https://user-images.githubusercontent.com/3804538/211128801-cfc29d61-f145-4fc3-a4f7-352f048e6cab.png">

