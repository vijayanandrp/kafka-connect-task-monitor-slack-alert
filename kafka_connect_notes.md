# About Kafka
Apache Kafka is a community distributed event streaming platform capable of handling trillions of events a day. Initially conceived as a messaging queue, Kafka is based on an abstraction of a distributed commit log. Since being created and open-sourced by LinkedIn in 2011, Kafka has quickly evolved from messaging queue to a full-fledged event streaming platform.  

Core components of Kafka Streaming Ecosystems are 
1. Kafka Cluster 
2. Kafka Connect (Distributed, Scalable and Fault tolerant same as Kafka)
3. ksqlDB
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

## How Kafka Connect Works
![image](https://user-images.githubusercontent.com/3804538/211220663-34f0749d-cd04-441c-b83e-d1eee4145dc1.png)

Kafka Connect runs in its own process, separate from the Kafka brokers. It is distributed, scalable, and fault tolerant, giving you the same features you know and love about Kafka itself.

But the best part of Kafka Connect is that using it requires no programming. It’s completely configuration-based, making it available to a wide range of users—not just developers. In addition to ingest and egress of data, Kafka Connect can also perform lightweight transformations on the data as it passes through.

Anytime you are looking to stream data into Kafka from another system, or stream data from Kafka to elsewhere, Kafka Connect should be the first thing that comes to mind.

Kafka connector polling the database for updates and translating the information into real-time events that it produces to Kafka.
Kafka sits between the source and target systems means that we’re building a loosely coupled system. In other words, it’s relatively easy for us to change the source or target without impacting the other.
Kafka stores data up to a configurable time interval per data entity (topic), it’s possible to stream the same original data to multiple downstream targets.

![image](https://user-images.githubusercontent.com/3804538/211223254-e6d433df-23a5-4a65-86b9-9219a6979cac.png)

When running Kafka Connect, instances of connector plugins provide the integration between external data systems and the Kafka Connect framework. These connector plugins are reusable components that define how source connectors ought to capture data from data sources to a Kafka topic and also how sink connectors should copy data from Kafka topics to be recognized by a target system. By taking care of all of this boilerplate logic for you, the plugins allow you to hit the ground running with Kafka Connect and focus on your data.

## inside-kafka-connect
Kafka Connect is built around a pluggable architecture of several components, which together provide very flexible integration pipelines. To get the most out of Kafka Connect it’s important to understand these components and their roles:
![image](https://user-images.githubusercontent.com/3804538/211227997-9cea298e-5589-4696-8cc9-97fd1f13ec75.png)

- Connectors are responsible for the interaction between Kafka Connect and the external technology it’s being integrated with
- Converters handle the serialization and deserialization of data
- Transformations can optionally apply one or more transformations to the data passing through the pipeline
## Connectors
![image](https://user-images.githubusercontent.com/3804538/211228323-f1aa2be7-40d3-4f62-a316-d1d0fd2b75e9.png)
It’s important to understand that the connector plugins themselves don't read from or write to (consume/produce) Kafka itself. The plugins just provide the interface between Kafka and the external technology. This is a deliberate design.

- Source connectors interface with the source API and extract the payload + schema of the data, and pass this internally as a generic representation of the data.
- Sink connectors work in reverse—they take a generic representation of the data, and the sink connector plugin writes that to the target system using its API.
Kafka Connect and its underlying components take care of writing data received from source connectors to Kafka topics as well as reading data from Kafka topics and passing it to sink connectors.

Now, this is all hidden from the user—when you add a new connector instance, that’s all you need to configure and Kafka Connect does the rest to get the data flowing. Converters are the next piece of the puzzle and it is important to understand them to help you avoid common pitfalls with Kafka Connect. 
- Connectors can be added using REST API, ksqlDB

## Converters Serialize/Deserialize the Data
![image](https://user-images.githubusercontent.com/3804538/211228357-6572c524-710a-48a7-a09a-3d5b6ad7e1ab.png)

Converters are responsible for the serialization and deserialization of data flowing between Kafka Connect and Kafka itself. You’ll sometimes see similar components referred to as SerDes (“SerializerDeserializer”) in Kafka Streams, or just plain old serializers and deserializers in the Kafka Client libraries.

There are a ton of different converters available, but some common ones include:
```
Avro – io.confluent.connect.avro.AvroConverter
Protobuf – io.confluent.connect.protobuf.ProtobufConverter
String – org.apache.kafka.connect.storage.StringConverter
JSON – org.apache.kafka.connect.json.JsonConverter
JSON Schema – io.confluent.connect.json.JsonSchemaConverter
ByteArray – org.apache.kafka.connect.converters.ByteArrayConverter
```
While Kafka doesn’t care about how you serialize your data (as far as it’s concerned, it’s just a series of bytes), you should care about how you serialize your data! In the same way that you would take a carefully considered approach to how you design your services and model your data, you should also be deliberate in your serialization approach.

![image](https://user-images.githubusercontent.com/3804538/211228416-7cb9ac94-05e7-42b9-969c-953c75039c25.png)

As well as managing the straightforward matter of serializing data flowing into Kafka and deserializing it on its way out, converters have a crucial role to play in the persistence of schemas. Almost all data that we deal with has a schema; it’s up to us whether we choose to acknowledge that in our designs or not. You can consider schemas as the API between applications and components of a pipeline. Schemas are the contract between one component in the pipeline and another, describing the shape and form of the data.

When you ingest data from a source such as a database, as well as the rows of data, you have the metadata that describes the fields—the data types, their names, etc. Having this schema metadata is valuable, and you will want to retain it in an efficient manner. A great way to do this is by using a serialization method such as Avro, Protobuf, or JSON Schema. All three of these will serialize the data onto a Kafka topic and then store the schema separately in the Confluent Schema Registry. By storing the schema for data, you can easily utilize it in your consuming applications and pipelines. You can also use it to enforce data hygiene in the pipeline by ensuring that only data that is compatible with the schema is stored on a given topic.

You can opt to use serialization formats that don’t store schemas like JSON, string, and byte array, and in some cases, these are valid. If you use these, just make sure that you are doing so for deliberate reasons and have considered how else you will handle schema information.

## Single-Message-Transforms

The third and final key component in Kafka Connect is the transform piece. Unlike connectors and converters, these are entirely optional. You can use them to modify data from a source connector before it is written to Kafka, and modify data read from Kafka before it’s written to the sink. Transforms operate over individual messages as they move, so they’re known as Single Message Transforms or SMTs.

![image](https://user-images.githubusercontent.com/3804538/211228568-716a9d44-b441-4594-84bb-a6b9f8d92ff5.png)

Common uses for SMTs include:

Dropping fields from data at ingest, such as personally identifiable information (PII) if specified by the system requirements
Adding metadata information such as lineage to data ingested through Kafka Connect
Changing field data types
Modifying the topic name to include a timestamp
Renaming fields

For more complex transformations, including aggregations and joins to other topics or lookups to other systems, a full stream processing layer in ksqlDB or Kafka Streams is recommended.

Kafka Connect runs under the Java virtual machine (JVM) as a process known as a worker. Each worker can execute multiple connectors. When you look to see if Kafka Connect is running, or want to look at its log file, it's the worker process that you're looking at. Tasks are executed by Kafka Connect workers.


A Kafka Connect worker can be run in one of two deployment modes: standalone or distributed. The way in which you configure and operate Kafka Connect in these two modes is different and each has its pros and cons.

Despite its name, the distributed deployment mode is equally valid for a single worker deployed in a sandbox or development environment. In this mode, Kafka Connect uses Kafka topics to store state pertaining to connector configuration, connector status, and more. The topics are configured to retain this information indefinitely, known as compacted topics. Connector instances are created and managed via the REST API that Kafka Connect offers.

The distributed mode is the recommended best practice for most use cases.

![image](https://user-images.githubusercontent.com/3804538/211229272-bdcecd4b-d914-412f-ab2f-3b272725e089.png)

Since all offsets, configs, and status information for the distributed mode cluster is maintained in Kafka topics, this means that you can add additional workers easily, as they can read everything that they need from Kafka. When you add workers from a Kafka Connect cluster, the tasks are rebalanced across the available workers to distribute the workload. If you decide to scale down your cluster (or even if something outside your control happens and a worker crashes), Kafka Connect will rebalance again to ensure that all the connector tasks are still executed.

![image](https://user-images.githubusercontent.com/3804538/211229315-db58d86c-45f0-4e64-96ce-4036d4f2787f.png)

![image](https://user-images.githubusercontent.com/3804538/211229330-5fd6d9ba-da13-48f8-9fbc-5cef91605424.png)

The minimum number of workers recommended is two so that you have fault tolerance. But of course, you can add additional workers to the cluster as your throughput needs increase. You can opt to have fewer, bigger clusters of workers, or you may choose to deploy a greater number of smaller clusters in order to physically isolate workloads. Both are valid approaches and are usually dictated by organizational structure and responsibility for the respective pipelines implemented in Kafka Connect.

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
