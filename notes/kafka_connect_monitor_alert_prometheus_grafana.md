
# Prometheus

Prometheus is a free software application used for event monitoring and alerting. It records real-time metrics in a time series database built using a HTTP pull model, with flexible queries and real-time alerting.

Prometheus is a tool used for aggregating multiple platform metrics while scraping hundreds of endpoints. It is purpose-built for scrape and aggregation use cases. Internally, it contains a time-series data store that allows you to store and retrieve time-sliced data in an optimized fashion. It also uses the OpenMetrics format, a CNCF Sandbox project that recently reached v1.0 and is expected to gain traction, with many tools supporting or planning to support it.
(The metric exporters created and leveraged by the Prometheus community already adhere to these standards.) 
Grafana is an open source charting and dashboarding tool that talks to Prometheus and renders beautiful graphs.

## How does Prometheus work?
Prometheus is an ecosystem with two major components: the server-side component and the client-side configuration. The server-side component is responsible for storing all the metrics and scraping all clients as well. Prometheus differs from services like Elasticsearch and Splunk, which generally use an intermediate component responsible for scraping data from clients and shipping it to the servers. Because there is no intermediate component scraping Prometheus metrics, all poll-related configurations are present on the server itself.

The process looks like this:

![image](https://user-images.githubusercontent.com/3804538/211356782-cdff05f8-978f-4eeb-9c27-4e8fcb2c44fb.png)

There are two core pieces in this diagram:

1.  **Prometheus server:** This component is responsible for polling all of the processes/clients with their metrics exposed on a specific port. The Prometheus server internally maintains a configuration file that lists all the server IP addresses/hostnames and ports on which Prometheus metrics are exposed. The scrape target configuration is the file that keeps all target mapping within Prometheus. Scrape targets are required when we are deploying everything manually without any automation. Prometheus also supports service discovery modules, which it can leverage to discover any available services that are exposing metrics. This auto-discovery is an amazing tool when used with Kubernetes-based deployments, where Pod names (among other elements) are ephemeral. To keep it simple, [Prometheus service discovery](https://github.com/prometheus/prometheus/tree/main/discovery) won’t be covered in this post.
2.  **Client processes:** All clients that want to leverage Prometheus will need two configuration pieces. First, they must use the Prometheus client library to expose metrics in a Prometheus compatible format (OpenMetrics). Secondly, they must use a YAML configuration file for extracting JMX metrics. This configuration file is used for converting, renaming, and filtering some of the attributes for consumption. The YAML configuration file is necessary for the JVM client, as the JVM MBeans are exposed, converted, and/or renamed to a specific format for consumption using this configuration file.

JMX exporter JAR file: This file is responsible for exposing all of the JVM metrics in a Prometheus-compatible format. The JAR file should be copied on all of the servers where Prometheus clients reside, and it will be activated using the Java agent switch on the command line for all components.

https://www.confluent.io/blog/monitor-kafka-clusters-with-prometheus-grafana-and-confluent/

# What is the Prometheus Node Exporter? 
The Prometheus Node Exporter is an open-source time-series monitoring and alerting system for cloud-native environments, including Kubernetes, hosted by the Cloud Native Computing Foundation (CNCF) on GitHub. It can collect and store node-level metrics as time-series data, recording information with a timestamp. It can also collect and record labels, which are optional key-value pairs. The Prometheus Node Exporter exposes a wide variety of hardware- and kernel-related metrics.

The statistics which are detailed in the table below are used to monitor system performance to avoid slow-down, outages, and troubleshoot node-level issues.

![image](https://user-images.githubusercontent.com/3804538/211332854-6f3b71c7-00ce-4ab0-b83c-994cb32265ad.png)

![image](https://user-images.githubusercontent.com/3804538/211333112-9b10c364-bf4c-4a14-8b95-8fa73499b625.png)


# Using JMX exporter to expose JMX metrics

Java Management Extensions (JMX) is a technology that provides the tools for providing monitoring within applications built on JVM. 

Since Kafka is written in Java, it extensively uses JMX technology to expose its internal metrics over the JMX platform.

JMX Exporter is a collector that can run as a part of an existing Java application (such as Kafka) and expose its JMX metrics over an HTTP endpoint, 
which can be consumed by any system such as Prometheus. 

JMX to Prometheus exporter: a collector that can configurably scrape and expose mBeans of a JMX target.

This exporter is intended to be run as a Java Agent, exposing a HTTP server and serving metrics of the local JVM. 
It can be also run as a standalone HTTP server and scrape remote JMX targets, 
but this has various disadvantages, such as being harder to configure and being unable to expose process metrics 
(e.g., memory and CPU usage). Running the exporter as a Java Agent is thus strongly encouraged.

# Grafana Open Source
> Grafana is a multi-platform open source analytics and interactive visualization web application. It provides charts, graphs, and alerts for the web when connected to supported data sources.

![image](https://user-images.githubusercontent.com/3804538/211333876-e6bee69a-cadf-4fdb-a73c-a757d66be021.png)

Grafana open source is open source visualization and analytics software. It allows you to query, visualize, alert on, and explore your metrics, logs, and traces no matter where they are stored. It provides you with tools to turn your time-series database (TSDB) data into insightful graphs and visualizations.

# Loki: like Prometheus, but for logs.

Loki is a horizontally-scalable, highly-available, multi-tenant log aggregation system inspired by [Prometheus](https://prometheus.io/).
It is designed to be very cost effective and easy to operate.
It does not index the contents of the logs, but rather a set of labels for each log stream.

Compared to other log aggregation systems, Loki:

- does not do full text indexing on logs. By storing compressed, unstructured logs and only indexing metadata, Loki is simpler to operate and cheaper to run.
- indexes and groups log streams using the same labels you’re already using with Prometheus, enabling you to seamlessly switch between metrics and logs using the same labels that you’re already using with Prometheus.
- is an especially good fit for storing [Kubernetes](https://kubernetes.io/) Pod logs. Metadata such as Pod labels is automatically scraped and indexed.
- has native support in Grafana (needs Grafana v6.0).

A Loki-based logging stack consists of 3 components:

- `promtail` is the agent, responsible for gathering logs and sending them to Loki.
- `loki` is the main server, responsible for storing logs and processing queries.
- [Grafana](https://github.com/grafana/grafana) for querying and displaying the logs.

Loki is like Prometheus, but for logs: we prefer a multidimensional label-based approach to indexing, and want a single-binary, easy to operate system with no dependencies.
Loki differs from Prometheus by focusing on logs instead of metrics, and delivering logs via push, instead of pull.

![Screenshot 2023-01-09 at 17 21 39](https://user-images.githubusercontent.com/3804538/211368810-1e3c1b64-2bdb-43db-afdb-8d9800c28c2a.png)

# References 
1. https://www.confluent.io/blog/monitor-kafka-clusters-with-prometheus-grafana-and-confluent/
