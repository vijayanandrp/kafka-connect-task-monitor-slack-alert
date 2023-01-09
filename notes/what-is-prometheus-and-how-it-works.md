
# What is Prometheus?
Prometheus is an open-source systems monitoring and alerting toolkit.
Prometheus collects and stores its metrics as time series data, 
i.e. metrics information is stored with the timestamp at which it was recorded, alongside optional key-value pairs called labels.

### History
- Prometheus toolkit originally built at SoundCloud. 
- Since its inception in 2012, many companies and organizations have adopted Prometheus, and the project has a very active developer and user community. 
- It is now a standalone open source project and maintained independently of any company. 
- To emphasize this, and to clarify the project's governance structure, Prometheus joined the Cloud Native Computing Foundation in 2016 as the second hosted project, after Kubernetes.

## Features
Prometheus's main features are:

- a multi-dimensional data model with time series data identified by metric name and key/value pairs
- **PromQL**, a flexible query language to leverage this dimensionality
- no reliance on distributed storage; single server nodes are autonomous
- time series collection happens via a pull model over HTTP
- pushing time series is supported via an intermediary gateway
- targets are discovered via service discovery or static configuration
- multiple modes of graphing and dashboarding support

### What are metrics ?
In layperson terms, metrics are _numeric_ measurements. 
_Time series_ means that changes are recorded over time. 
What users want to measure differs from application to application. 
For a web server it might be request times, for a database it might be number of active connections or number of active queries etc.
