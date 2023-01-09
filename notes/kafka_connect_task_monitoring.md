

# What is the Prometheus Node Exporter? 
The Prometheus Node Exporter is an open-source time-series monitoring and alerting system for cloud-native environments, including Kubernetes, hosted by the Cloud Native Computing Foundation (CNCF) on GitHub. It can collect and store node-level metrics as time-series data, recording information with a timestamp. It can also collect and record labels, which are optional key-value pairs. The Prometheus Node Exporter exposes a wide variety of hardware- and kernel-related metrics.

The statistics which are detailed in the table below are used to monitor system performance to avoid slow-down, outages, and troubleshoot node-level issues.

![image](https://user-images.githubusercontent.com/3804538/211332854-6f3b71c7-00ce-4ab0-b83c-994cb32265ad.png)


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

