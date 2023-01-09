

## Using JMX exporter to expose JMX metrics
Java Management Extensions (JMX) is a technology that provides the tools for providing monitoring within applications built on JVM. 

Since Kafka is written in Java, it extensively uses JMX technology to expose its internal metrics over the JMX platform.

JMX Exporter is a collector that can run as a part of an existing Java application (such as Kafka) and expose its JMX metrics over an HTTP endpoint, 
which can be consumed by any system such as Prometheus. 

JMX to Prometheus exporter: a collector that can configurably scrape and expose mBeans of a JMX target.
This exporter is intended to be run as a Java Agent, exposing a HTTP server and serving metrics of the local JVM. 
It can be also run as a standalone HTTP server and scrape remote JMX targets, 
but this has various disadvantages, such as being harder to configure and being unable to expose process metrics 
(e.g., memory and CPU usage). Running the exporter as a Java Agent is thus strongly encouraged.

