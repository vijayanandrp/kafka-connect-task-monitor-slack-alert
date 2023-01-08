# About Kafka
Apache Kafka is a community distributed event streaming platform capable of handling trillions of events a day. Initially conceived as a messaging queue, Kafka is based on an abstraction of a distributed commit log. Since being created and open-sourced by LinkedIn in 2011, Kafka has quickly evolved from messaging queue to a full-fledged event streaming platform. Kafka stores data up to a configurable time interval per data entity of kafka topic.

Core components of Kafka Streaming Ecosystems are 
1. Kafka Cluster (Distributed)
2. Kafka Connect (Distributed, Scalable and Fault tolerant same as Kafka)
3. kSQL DB
4. Schema Registry 

![image](https://user-images.githubusercontent.com/3804538/211220554-577a24b7-dd10-45b7-a737-80ed8836b7ad.png)


# Kafka Connect 

Kafka Connect is a component of Apache Kafka® that’s used to perform streaming integration between Kafka and other systems such as databases, cloud services, search indexes, file systems, and key-value stores.

![image](https://user-images.githubusercontent.com/3804538/211216875-2f1cbf7d-57c1-436f-b631-6d7f48995fd2.png)


If you’re new to Kafka, you may want to take a look at the Apache Kafka 101 course before you get started with this course.

Kafka Connect makes it easy to stream data from numerous sources into Kafka, and stream data out of Kafka to numerous targets. 

The diagram you see here shows a small sample of these sources and sinks (targets). There are literally hundreds of different connectors available for Kafka Connect. Some of the most popular ones include:

* RDBMS (Oracle, SQL Server, Db2, Postgres, MySQL)
* Cloud object stores (Amazon S3, Azure Blob Storage, Google Cloud Storage)
* Message queues (ActiveMQ, IBM MQ, RabbitMQ)
* NoSQL and document stores (Elasticsearch, MongoDB, Cassandra)
* Cloud data warehouses (Snowflake, Google BigQuery, Amazon Redshift)

![image](https://user-images.githubusercontent.com/3804538/211218683-3a1fecec-b5a6-43a6-96b5-3a028d7870b5.png)


REST API - [https://docs.confluent.io/platform/current/connect/references/restapi.html#topics](https://docs.confluent.io/platform/current/connect/references/restapi.html#topics)

### Ansible to monitor and restart Kafka Connect (one time process)
Stackoverflow - [https://stackoverflow.com/questions/72545501/ansible-loop-based-on-fact-to-restart-kafka-connector-failed-tasks](https://stackoverflow.com/questions/72545501/ansible-loop-based-on-fact-to-restart-kafka-connector-failed-tasks)

```ansible
tasks:
    - name: Gethering Connector Names
      uri:
        url: "{{scheme }}://{{ server }}:{{ port_no }}/connectors"
        user: "{{ username }}"
        password: "{{ password }}"
        method: GET
        force_basic_auth: yes
        status_code: 200
      register: conn_stat
    - name: Checking for Connector status
      uri:
        url: "{{scheme }}://{{ server }}:{{ port_no }}/connectors/{{ abc_conn_name }}/status"
        user: "{{ username }}"
        password: "{{ password }}"
        method: GET
        force_basic_auth: yes
      loop: "{{ conn_name }}"
      loop_control:
        loop_var: abc_conn_name
      vars:
        conn_name: "{{ conn_stat.json }}"
      register: conn_stat_1
    - name: Restart Connector Failed tasks
      vars:
        failed_connector_name_task_id: "{{ conn_stat_1 | json_query('results[].json[].{name: name ,id: [tasks[?state == `RUNNING`].id [] | [0] ]}') }}"
      uri:
        url: "{{scheme }}://{{ server }}:{{ port_no }}/connectors/{{ item.0.name }}/tasks/{{ item.1 }}/restart"
        user: "{{ username }}"
        password: "{{ password }}"
        method: POST
        force_basic_auth: yes
        status_code: 200
      loop: "{{ failed_connector_name_task_id | subelements('id', skip_missing=True) }}"
```

### Automatically restarting failed Kafka Connect tasks with REST API (Curl, Bash script) 

Here’s a hacky way to automatically restart Kafka Connect connectors if they fail. 
Restarting automatically only makes sense if it’s a _transient failure_; if there’s a problem with your pipeline 
(e.g. bad records or a mis-configured server) then you don’t gain anything from this. 

```bash
#!/usr/bin/env bash
# @rmoff / June 6, 2019

echo '----'
# Set the path so cron can find jq, necessary for cron depending on your default PATH
export PATH=$PATH:/usr/local/bin/

# What time is it Mr Wolf? 
`date` 

# List current connectors and status
curl -s "http://localhost:8083/connectors?expand=info&expand=status" | \
           jq '. | to_entries[] | [ .value.info.type, .key, .value.status.connector.state,.value.status.tasks[].state,.value.info.config."connector.class"]|join(":|:")' | \
           column -s : -t| sed 's/\"//g'| sort


# Restart any connector tasks that are FAILED
# Works for Apache Kafka >= 2.3.0 
# Thanks to @jocelyndrean for this enhanced code snippet that also supports 
#  multiple tasks in a connector
curl -s "http://localhost:8083/connectors?expand=status" | \
  jq -c -M 'map({name: .status.name } +  {tasks: .status.tasks}) | .[] | {task: ((.tasks[]) + {name: .name})}  | select(.task.state=="FAILED") | {name: .task.name, task_id: .task.id|tostring} | ("/connectors/"+ .name + "/tasks/" + .task_id + "/restart")' | \
  xargs -I{connector_and_task} curl -v -X POST "http://localhost:8083"\{connector_and_task\}
```

Which as any hacky admin will know can be scheduled to run with a crontab such as this:

`*/5 * * * * /u01/connectors/restart_failed_connector_tasks.sh 2>&1 >> /u01/connectors/connect_monitor.log`

Now every five minutes the script will look for any FAILED tasks and send a REST call to restart them.

Soucre = [https://rmoff.net/2019/06/06/automatically-restarting-failed-kafka-connect-tasks/](https://rmoff.net/2019/06/06/automatically-restarting-failed-kafka-connect-tasks/)
