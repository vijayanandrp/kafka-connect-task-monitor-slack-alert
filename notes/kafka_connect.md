https://kafka.apache.org/documentation.html#connect_overview

### [8.1 Overview](#connect_overview)

Kafka Connect is a tool for scalably and reliably streaming data between Apache Kafka and other systems. It makes it simple to quickly define _connectors_ that move large collections of data into and out of Kafka. Kafka Connect can ingest entire databases or collect metrics from all your application servers into Kafka topics, making the data available for stream processing with low latency. An export job can deliver data from Kafka topics into secondary storage and query systems or into batch systems for offline analysis.

Kafka Connect features include:

* **A common framework for Kafka connectors** \- Kafka Connect standardizes integration of other data systems with Kafka, simplifying connector development, deployment, and management
* **Distributed and standalone modes** \- scale up to a large, centrally managed service supporting an entire organization or scale down to development, testing, and small production deployments
* **REST interface** \- submit and manage connectors to your Kafka Connect cluster via an easy to use REST API
* **Automatic offset management** \- with just a little information from connectors, Kafka Connect can manage the offset commit process automatically so connector developers do not need to worry about this error prone part of connector development
* **Distributed and scalable by default** \- Kafka Connect builds on the existing group management protocol. More workers can be added to scale up a Kafka Connect cluster.
* **Streaming/batch integration** \- leveraging Kafka's existing capabilities, Kafka Connect is an ideal solution for bridging streaming and batch data systems

### [8.2 User Guide](#connect_user)

The [quickstart](../quickstart) provides a brief example of how to run a standalone version of Kafka Connect. This section describes how to configure, run, and manage Kafka Connect in more detail.

#### [Running Kafka Connect](#connect_running)

Kafka Connect currently supports two modes of execution: standalone (single process) and distributed.

In standalone mode all work is performed in a single process. This configuration is simpler to setup and get started with and may be useful in situations where only one worker makes sense (e.g. collecting log files), but it does not benefit from some of the features of Kafka Connect such as fault tolerance. You can start a standalone process with the following command:

\> bin/connect-standalone.sh config/connect-standalone.properties connector1.properties \[connector2.properties ...\]

The first parameter is the configuration for the worker. This includes settings such as the Kafka connection parameters, serialization format, and how frequently to commit offsets. The provided example should work well with a local cluster running with the default configuration provided by `config/server.properties`. It will require tweaking to use with a different configuration or production deployment. All workers (both standalone and distributed) require a few configs:

* `bootstrap.servers` \- List of Kafka servers used to bootstrap connections to Kafka
* `key.converter` \- Converter class used to convert between Kafka Connect format and the serialized form that is written to Kafka. This controls the format of the keys in messages written to or read from Kafka, and since this is independent of connectors it allows any connector to work with any serialization format. Examples of common formats include JSON and Avro.
* `value.converter` \- Converter class used to convert between Kafka Connect format and the serialized form that is written to Kafka. This controls the format of the values in messages written to or read from Kafka, and since this is independent of connectors it allows any connector to work with any serialization format. Examples of common formats include JSON and Avro.
* `plugin.path` (default `empty`) \- a list of paths that contain Connect plugins (connectors, converters, transformations). Before running quick starts, users must add the absolute path that contains the example FileStreamSourceConnector and FileStreamSinkConnector packaged in `connect-file-"version".jar`, because these connectors are not included by default to the `CLASSPATH` or the `plugin.path` of the Connect worker (see [plugin.path](#connectconfigs_plugin.path) property for examples).

The important configuration options specific to standalone mode are:

* `offset.storage.file.filename` \- File to store offset data in

The parameters that are configured here are intended for producers and consumers used by Kafka Connect to access the configuration, offset and status topics. For configuration of the producers used by Kafka source tasks and the consumers used by Kafka sink tasks, the same parameters can be used but need to be prefixed with `producer.` and `consumer.` respectively. The only Kafka client parameter that is inherited without a prefix from the worker configuration is `bootstrap.servers`, which in most cases will be sufficient, since the same cluster is often used for all purposes. A notable exception is a secured cluster, which requires extra parameters to allow connections. These parameters will need to be set up to three times in the worker configuration, once for management access, once for Kafka sources and once for Kafka sinks.

Starting with 2.3.0, client configuration overrides can be configured individually per connector by using the prefixes `producer.override.` and `consumer.override.` for Kafka sources or Kafka sinks respectively. These overrides are included with the rest of the connector's configuration properties.

The remaining parameters are connector configuration files. You may include as many as you want, but all will execute within the same process (on different threads).

Distributed mode handles automatic balancing of work, allows you to scale up (or down) dynamically, and offers fault tolerance both in the active tasks and for configuration and offset commit data. Execution is very similar to standalone mode:

\> bin/connect-distributed.sh config/connect-distributed.properties

The difference is in the class which is started and the configuration parameters which change how the Kafka Connect process decides where to store configurations, how to assign work, and where to store offsets and task statues. In the distributed mode, Kafka Connect stores the offsets, configs and task statuses in Kafka topics. It is recommended to manually create the topics for offset, configs and statuses in order to achieve the desired the number of partitions and replication factors. If the topics are not yet created when starting Kafka Connect, the topics will be auto created with default number of partitions and replication factor, which may not be best suited for its usage.

In particular, the following configuration parameters, in addition to the common settings mentioned above, are critical to set before starting your cluster:

* `group.id` (default `connect-cluster`) \- unique name for the cluster, used in forming the Connect cluster group; note that this **must not conflict** with consumer group IDs
* `config.storage.topic` (default `connect-configs`) \- topic to use for storing connector and task configurations; note that this should be a single partition, highly replicated, compacted topic. You may need to manually create the topic to ensure the correct configuration as auto created topics may have multiple partitions or be automatically configured for deletion rather than compaction
* `offset.storage.topic` (default `connect-offsets`) \- topic to use for storing offsets; this topic should have many partitions, be replicated, and be configured for compaction
* `status.storage.topic` (default `connect-status`) \- topic to use for storing statuses; this topic can have multiple partitions, and should be replicated and configured for compaction

Note that in distributed mode the connector configurations are not passed on the command line. Instead, use the REST API described below to create, modify, and destroy connectors.

#### [Configuring Connectors](#connect_configuring)

Connector configurations are simple key-value mappings. For standalone mode these are defined in a properties file and passed to the Connect process on the command line. In distributed mode, they will be included in the JSON payload for the request that creates (or modifies) the connector.

Most configurations are connector dependent, so they can't be outlined here. However, there are a few common options:

* `name` \- Unique name for the connector. Attempting to register again with the same name will fail.
* `connector.class` \- The Java class for the connector
* `tasks.max` \- The maximum number of tasks that should be created for this connector. The connector may create fewer tasks if it cannot achieve this level of parallelism.
* `key.converter` \- (optional) Override the default key converter set by the worker.
* `value.converter` \- (optional) Override the default value converter set by the worker.

The `connector.class` config supports several formats: the full name or alias of the class for this connector. If the connector is org.apache.kafka.connect.file.FileStreamSinkConnector, you can either specify this full name or use FileStreamSink or FileStreamSinkConnector to make the configuration a bit shorter.

Sink connectors also have a few additional options to control their input. Each sink connector must set one of the following:

* `topics` \- A comma-separated list of topics to use as input for this connector
* `topics.regex` \- A Java regular expression of topics to use as input for this connector

For any other options, you should consult the documentation for the connector.

#### [Transformations](#connect_transforms)

Connectors can be configured with transformations to make lightweight message-at-a-time modifications. They can be convenient for data massaging and event routing.

A transformation chain can be specified in the connector configuration.

* `transforms` \- List of aliases for the transformation, specifying the order in which the transformations will be applied.
* `transforms.$alias.type` \- Fully qualified class name for the transformation.
* `transforms.$alias.$transformationSpecificConfig` Configuration properties for the transformation

For example, lets take the built-in file source connector and use a transformation to add a static field.

Throughout the example we'll use schemaless JSON data format. To use schemaless format, we changed the following two lines in `connect-standalone.properties` from true to false:

key.converter.schemas.enable
value.converter.schemas.enable

The file source connector reads each line as a String. We will wrap each line in a Map and then add a second field to identify the origin of the event. To do this, we use two transformations:

* **HoistField** to place the input line inside a Map
* **InsertField** to add the static field. In this example we'll indicate that the record came from a file connector

After adding the transformations, `connect-file-source.properties` file looks as following:

name=local-file-source
connector.class=FileStreamSource
tasks.max=1
file=test.txt
topic=connect-test
transforms=MakeMap, InsertSource
transforms.MakeMap.type=org.apache.kafka.connect.transforms.HoistField$Value
transforms.MakeMap.field=line
transforms.InsertSource.type=org.apache.kafka.connect.transforms.InsertField$Value
transforms.InsertSource.static.field=data_source
transforms.InsertSource.static.value=test-file-source

All the lines starting with `transforms` were added for the transformations. You can see the two transformations we created: "InsertSource" and "MakeMap" are aliases that we chose to give the transformations. The transformation types are based on the list of built-in transformations you can see below. Each transformation type has additional configuration: HoistField requires a configuration called "field", which is the name of the field in the map that will include the original String from the file. InsertField transformation lets us specify the field name and the value that we are adding.

When we ran the file source connector on my sample file without the transformations, and then read them using `kafka-console-consumer.sh`, the results were:

"foo"
"bar"
"hello world"

We then create a new file connector, this time after adding the transformations to the configuration file. This time, the results will be:

{"line":"foo","data_source":"test-file-source"}
{"line":"bar","data_source":"test-file-source"}
{"line":"hello world","data_source":"test-file-source"}

You can see that the lines we've read are now part of a JSON map, and there is an extra field with the static value we specified. This is just one example of what you can do with transformations.

##### [Included transformations](#connect_included_transformation)

Several widely-applicable data and routing transformations are included with Kafka Connect:

* InsertField - Add a field using either static data or record metadata
* ReplaceField - Filter or rename fields
* MaskField - Replace field with valid null value for the type (0, empty string, etc) or custom replacement (non-empty string or numeric value only)
* ValueToKey - Replace the record key with a new key formed from a subset of fields in the record value
* HoistField - Wrap the entire event as a single field inside a Struct or a Map
* ExtractField - Extract a specific field from Struct and Map and include only this field in results
* SetSchemaMetadata - modify the schema name or version
* TimestampRouter - Modify the topic of a record based on original topic and timestamp. Useful when using a sink that needs to write to different tables or indexes based on timestamps
* RegexRouter - modify the topic of a record based on original topic, replacement string and a regular expression
* Filter - Removes messages from all further processing. This is used with a [predicate](#connect_predicates) to selectively filter certain messages.
* InsertHeader - Add a header using static data
* HeadersFrom - Copy or move fields in the key or value to the record headers
* DropHeaders - Remove headers by name

Details on how to configure each transformation are listed below:

##### [org.apache.kafka.connect.transforms.InsertField](#org.apache.kafka.connect.transforms.InsertField)

Insert field(s) using attributes from the record metadata or a configured static value.

Use the concrete transformation type designed for the record key (`org.apache.kafka.connect.transforms.InsertField$Key`) or value (`org.apache.kafka.connect.transforms.InsertField$Value`).

* ###### [offset.field](#org.apache.kafka.connect.transforms.InsertField_offset.field)
    
    Field name for Kafka offset - only applicable to sink connectors.  
    Suffix with `!` to make this a required field, or `?` to keep it optional (the default).
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | null |
    | Valid Values: |     |
    | Importance: | medium |
    
* ###### [partition.field](#org.apache.kafka.connect.transforms.InsertField_partition.field)
    
    Field name for Kafka partition. Suffix with `!` to make this a required field, or `?` to keep it optional (the default).
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | null |
    | Valid Values: |     |
    | Importance: | medium |
    
* ###### [static.field](#org.apache.kafka.connect.transforms.InsertField_static.field)
    
    Field name for static data field. Suffix with `!` to make this a required field, or `?` to keep it optional (the default).
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | null |
    | Valid Values: |     |
    | Importance: | medium |
    
* ###### [static.value](#org.apache.kafka.connect.transforms.InsertField_static.value)
    
    Static field value, if field name configured.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | null |
    | Valid Values: |     |
    | Importance: | medium |
    
* ###### [timestamp.field](#org.apache.kafka.connect.transforms.InsertField_timestamp.field)
    
    Field name for record timestamp. Suffix with `!` to make this a required field, or `?` to keep it optional (the default).
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | null |
    | Valid Values: |     |
    | Importance: | medium |
    
* ###### [topic.field](#org.apache.kafka.connect.transforms.InsertField_topic.field)
    
    Field name for Kafka topic. Suffix with `!` to make this a required field, or `?` to keep it optional (the default).
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | null |
    | Valid Values: |     |
    | Importance: | medium |
    

##### [org.apache.kafka.connect.transforms.ReplaceField](#org.apache.kafka.connect.transforms.ReplaceField)

Filter or rename fields.

Use the concrete transformation type designed for the record key (`org.apache.kafka.connect.transforms.ReplaceField$Key`) or value (`org.apache.kafka.connect.transforms.ReplaceField$Value`).

* ###### [exclude](#org.apache.kafka.connect.transforms.ReplaceField_exclude)
    
    Fields to exclude. This takes precedence over the fields to include.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: | ""  |
    | Valid Values: |     |
    | Importance: | medium |
    
* ###### [include](#org.apache.kafka.connect.transforms.ReplaceField_include)
    
    Fields to include. If specified, only these fields will be used.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: | ""  |
    | Valid Values: |     |
    | Importance: | medium |
    
* ###### [renames](#org.apache.kafka.connect.transforms.ReplaceField_renames)
    
    Field rename mappings.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: | ""  |
    | Valid Values: | list of colon-delimited pairs, e.g. `foo:bar,abc:xyz` |
    | Importance: | medium |
    
* ###### [blacklist](#org.apache.kafka.connect.transforms.ReplaceField_blacklist)
    
    Deprecated. Use exclude instead.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: | null |
    | Valid Values: |     |
    | Importance: | low |
    
* ###### [whitelist](#org.apache.kafka.connect.transforms.ReplaceField_whitelist)
    
    Deprecated. Use include instead.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: | null |
    | Valid Values: |     |
    | Importance: | low |
    

##### [org.apache.kafka.connect.transforms.MaskField](#org.apache.kafka.connect.transforms.MaskField)

Mask specified fields with a valid null value for the field type (i.e. 0, false, empty string, and so on).

For numeric and string fields, an optional replacement value can be specified that is converted to the correct type.

Use the concrete transformation type designed for the record key (`org.apache.kafka.connect.transforms.MaskField$Key`) or value (`org.apache.kafka.connect.transforms.MaskField$Value`).

* ###### [fields](#org.apache.kafka.connect.transforms.MaskField_fields)
    
    Names of fields to mask.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: |     |
    | Valid Values: | non-empty list |
    | Importance: | high |
    
* ###### [replacement](#org.apache.kafka.connect.transforms.MaskField_replacement)
    
    Custom value replacement, that will be applied to all 'fields' values (numeric or non-empty string values only).
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | null |
    | Valid Values: | non-empty string |
    | Importance: | low |
    

##### [org.apache.kafka.connect.transforms.ValueToKey](#org.apache.kafka.connect.transforms.ValueToKey)

Replace the record key with a new key formed from a subset of fields in the record value.

* ###### [fields](#org.apache.kafka.connect.transforms.ValueToKey_fields)
    
    Field names on the record value to extract as the record key.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: |     |
    | Valid Values: | non-empty list |
    | Importance: | high |
    

##### [org.apache.kafka.connect.transforms.HoistField](#org.apache.kafka.connect.transforms.HoistField)

Wrap data using the specified field name in a Struct when schema present, or a Map in the case of schemaless data.

Use the concrete transformation type designed for the record key (`org.apache.kafka.connect.transforms.HoistField$Key`) or value (`org.apache.kafka.connect.transforms.HoistField$Value`).

* ###### [field](#org.apache.kafka.connect.transforms.HoistField_field)
    
    Field name for the single field that will be created in the resulting Struct or Map.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: |     |
    | Valid Values: |     |
    | Importance: | medium |
    

##### [org.apache.kafka.connect.transforms.ExtractField](#org.apache.kafka.connect.transforms.ExtractField)

Extract the specified field from a Struct when schema present, or a Map in the case of schemaless data. Any null values are passed through unmodified.

Use the concrete transformation type designed for the record key (`org.apache.kafka.connect.transforms.ExtractField$Key`) or value (`org.apache.kafka.connect.transforms.ExtractField$Value`).

* ###### [field](#org.apache.kafka.connect.transforms.ExtractField_field)
    
    Field name to extract.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: |     |
    | Valid Values: |     |
    | Importance: | medium |
    

##### [org.apache.kafka.connect.transforms.SetSchemaMetadata](#org.apache.kafka.connect.transforms.SetSchemaMetadata)

Set the schema name, version or both on the record's key (`org.apache.kafka.connect.transforms.SetSchemaMetadata$Key`) or value (`org.apache.kafka.connect.transforms.SetSchemaMetadata$Value`) schema.

* ###### [schema.name](#org.apache.kafka.connect.transforms.SetSchemaMetadata_schema.name)
    
    Schema name to set.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | null |
    | Valid Values: |     |
    | Importance: | high |
    
* ###### [schema.version](#org.apache.kafka.connect.transforms.SetSchemaMetadata_schema.version)
    
    Schema version to set.
    
    |     |     |
    | --- | --- |
    | Type: | int |
    | Default: | null |
    | Valid Values: |     |
    | Importance: | high |
    

##### [org.apache.kafka.connect.transforms.TimestampRouter](#org.apache.kafka.connect.transforms.TimestampRouter)

Update the record's topic field as a function of the original topic value and the record timestamp.

This is mainly useful for sink connectors, since the topic field is often used to determine the equivalent entity name in the destination system(e.g. database table or search index name).

* ###### [timestamp.format](#org.apache.kafka.connect.transforms.TimestampRouter_timestamp.format)
    
    Format string for the timestamp that is compatible with `java.text.SimpleDateFormat`.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | yyyyMMdd |
    | Valid Values: |     |
    | Importance: | high |
    
* ###### [topic.format](#org.apache.kafka.connect.transforms.TimestampRouter_topic.format)
    
    Format string which can contain `${topic}` and `${timestamp}` as placeholders for the topic and timestamp, respectively.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | ${topic}-${timestamp} |
    | Valid Values: |     |
    | Importance: | high |
    

##### [org.apache.kafka.connect.transforms.RegexRouter](#org.apache.kafka.connect.transforms.RegexRouter)

Update the record topic using the configured regular expression and replacement string.

Under the hood, the regex is compiled to a `java.util.regex.Pattern`. If the pattern matches the input topic, `java.util.regex.Matcher#replaceFirst()` is used with the replacement string to obtain the new topic.

* ###### [regex](#org.apache.kafka.connect.transforms.RegexRouter_regex)
    
    Regular expression to use for matching.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: |     |
    | Valid Values: | valid regex |
    | Importance: | high |
    
* ###### [replacement](#org.apache.kafka.connect.transforms.RegexRouter_replacement)
    
    Replacement string.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: |     |
    | Valid Values: |     |
    | Importance: | high |
    

##### [org.apache.kafka.connect.transforms.Flatten](#org.apache.kafka.connect.transforms.Flatten)

Flatten a nested data structure, generating names for each field by concatenating the field names at each level with a configurable delimiter character. Applies to Struct when schema present, or a Map in the case of schemaless data. Array fields and their contents are not modified. The default delimiter is '.'.

Use the concrete transformation type designed for the record key (`org.apache.kafka.connect.transforms.Flatten$Key`) or value (`org.apache.kafka.connect.transforms.Flatten$Value`).

* ###### [delimiter](#org.apache.kafka.connect.transforms.Flatten_delimiter)
    
    Delimiter to insert between field names from the input record when generating field names for the output record
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | .   |
    | Valid Values: |     |
    | Importance: | medium |
    

##### [org.apache.kafka.connect.transforms.Cast](#org.apache.kafka.connect.transforms.Cast)

Cast fields or the entire key or value to a specific type, e.g. to force an integer field to a smaller width. Cast from integers, floats, boolean and string to any other type, and cast binary to string (base64 encoded).

Use the concrete transformation type designed for the record key (`org.apache.kafka.connect.transforms.Cast$Key`) or value (`org.apache.kafka.connect.transforms.Cast$Value`).

* ###### [spec](#org.apache.kafka.connect.transforms.Cast_spec)
    
    List of fields and the type to cast them to of the form field1:type,field2:type to cast fields of Maps or Structs. A single type to cast the entire value. Valid types are int8, int16, int32, int64, float32, float64, boolean, and string. Note that binary fields can only be cast to string.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: |     |
    | Valid Values: | list of colon-delimited pairs, e.g. `foo:bar,abc:xyz` |
    | Importance: | high |
    

##### [org.apache.kafka.connect.transforms.TimestampConverter](#org.apache.kafka.connect.transforms.TimestampConverter)

Convert timestamps between different formats such as Unix epoch, strings, and Connect Date/Timestamp types.Applies to individual fields or to the entire value.

Use the concrete transformation type designed for the record key (`org.apache.kafka.connect.transforms.TimestampConverter$Key`) or value (`org.apache.kafka.connect.transforms.TimestampConverter$Value`).

* ###### [target.type](#org.apache.kafka.connect.transforms.TimestampConverter_target.type)
    
    The desired timestamp representation: string, unix, Date, Time, or Timestamp
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: |     |
    | Valid Values: | \[string, unix, Date, Time, Timestamp\] |
    | Importance: | high |
    
* ###### [field](#org.apache.kafka.connect.transforms.TimestampConverter_field)
    
    The field containing the timestamp, or empty if the entire value is a timestamp
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | ""  |
    | Valid Values: |     |
    | Importance: | high |
    
* ###### [format](#org.apache.kafka.connect.transforms.TimestampConverter_format)
    
    A SimpleDateFormat-compatible format for the timestamp. Used to generate the output when type=string or used to parse the input if the input is a string.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | ""  |
    | Valid Values: |     |
    | Importance: | medium |
    
* ###### [unix.precision](#org.apache.kafka.connect.transforms.TimestampConverter_unix.precision)
    
    The desired Unix precision for the timestamp: seconds, milliseconds, microseconds, or nanoseconds. Used to generate the output when type=unix or used to parse the input if the input is a Long.Note: This SMT will cause precision loss during conversions from, and to, values with sub-millisecond components.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: | milliseconds |
    | Valid Values: | \[nanoseconds, microseconds, milliseconds, seconds\] |
    | Importance: | low |
    

##### [org.apache.kafka.connect.transforms.Filter](#org.apache.kafka.connect.transforms.Filter)

Drops all records, filtering them from subsequent transformations in the chain. This is intended to be used conditionally to filter out records matching (or not matching) a particular Predicate.

##### [org.apache.kafka.connect.transforms.InsertHeader](#org.apache.kafka.connect.transforms.InsertHeader)

Add a header to each record.

* ###### [header](#org.apache.kafka.connect.transforms.InsertHeader_header)
    
    The name of the header.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: |     |
    | Valid Values: | non-null string |
    | Importance: | high |
    
* ###### [value.literal](#org.apache.kafka.connect.transforms.InsertHeader_value.literal)
    
    The literal value that is to be set as the header value on all records.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: |     |
    | Valid Values: | non-null string |
    | Importance: | high |
    

##### [org.apache.kafka.connect.transforms.DropHeaders](#org.apache.kafka.connect.transforms.DropHeaders)

Removes one or more headers from each record.

* ###### [headers](#org.apache.kafka.connect.transforms.DropHeaders_headers)
    
    The name of the headers to be removed.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: |     |
    | Valid Values: | non-empty list |
    | Importance: | high |
    

##### [org.apache.kafka.connect.transforms.HeaderFrom](#org.apache.kafka.connect.transforms.HeaderFrom)

Moves or copies fields in the key/value of a record into that record's headers. Corresponding elements of `fields` and `headers` together identify a field and the header it should be moved or copied to. Use the concrete transformation type designed for the record key (`org.apache.kafka.connect.transforms.HeaderFrom$Key`) or value (`org.apache.kafka.connect.transforms.HeaderFrom$Value`).

* ###### [fields](#org.apache.kafka.connect.transforms.HeaderFrom_fields)
    
    Field names in the record whose values are to be copied or moved to headers.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: |     |
    | Valid Values: | non-empty list |
    | Importance: | high |
    
* ###### [headers](#org.apache.kafka.connect.transforms.HeaderFrom_headers)
    
    Header names, in the same order as the field names listed in the fields configuration property.
    
    |     |     |
    | --- | --- |
    | Type: | list |
    | Default: |     |
    | Valid Values: | non-empty list |
    | Importance: | high |
    
* ###### [operation](#org.apache.kafka.connect.transforms.HeaderFrom_operation)
    
    Either `move` if the fields are to be moved to the headers (removed from the key/value), or `copy` if the fields are to be copied to the headers (retained in the key/value).
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: |     |
    | Valid Values: | \[move, copy\] |
    | Importance: | high |
    

##### [Predicates](#connect_predicates)

Transformations can be configured with predicates so that the transformation is applied only to messages which satisfy some condition. In particular, when combined with the **Filter** transformation predicates can be used to selectively filter out certain messages.

Predicates are specified in the connector configuration.

* `predicates` \- Set of aliases for the predicates to be applied to some of the transformations.
* `predicates.$alias.type` \- Fully qualified class name for the predicate.
* `predicates.$alias.$predicateSpecificConfig` \- Configuration properties for the predicate.

All transformations have the implicit config properties `predicate` and `negate`. A predicular predicate is associated with a transformation by setting the transformation's `predicate` config to the predicate's alias. The predicate's value can be reversed using the `negate` configuration property.

For example, suppose you have a source connector which produces messages to many different topics and you want to:

* filter out the messages in the 'foo' topic entirely
* apply the ExtractField transformation with the field name 'other_field' to records in all topics _except_ the topic 'bar'

To do this we need first to filter out the records destined for the topic 'foo'. The Filter transformation removes records from further processing, and can use the TopicNameMatches predicate to apply the transformation only to records in topics which match a certain regular expression. TopicNameMatches's only configuration property is `pattern` which is a Java regular expression for matching against the topic name. The configuration would look like this:

transforms=Filter
transforms.Filter.type=org.apache.kafka.connect.transforms.Filter
transforms.Filter.predicate=IsFoo

predicates=IsFoo
predicates.IsFoo.type=org.apache.kafka.connect.transforms.predicates.TopicNameMatches
predicates.IsFoo.pattern=foo

Next we need to apply ExtractField only when the topic name of the record is not 'bar'. We can't just use TopicNameMatches directly, because that would apply the transformation to matching topic names, not topic names which do _not_ match. The transformation's implicit `negate` config properties allows us to invert the set of records which a predicate matches. Adding the configuration for this to the previous example we arrive at:

transforms=Filter,Extract
transforms.Filter.type=org.apache.kafka.connect.transforms.Filter
transforms.Filter.predicate=IsFoo

transforms.Extract.type=org.apache.kafka.connect.transforms.ExtractField$Key
transforms.Extract.field=other_field
transforms.Extract.predicate=IsBar
transforms.Extract.negate=true

predicates=IsFoo,IsBar
predicates.IsFoo.type=org.apache.kafka.connect.transforms.predicates.TopicNameMatches
predicates.IsFoo.pattern=foo

predicates.IsBar.type=org.apache.kafka.connect.transforms.predicates.TopicNameMatches
predicates.IsBar.pattern=bar

Kafka Connect includes the following predicates:

* `TopicNameMatches` \- matches records in a topic with a name matching a particular Java regular expression.
* `HasHeaderKey` \- matches records which have a header with the given key.
* `RecordIsTombstone` \- matches tombstone records, that is records with a null value.

Details on how to configure each predicate are listed below:

##### [org.apache.kafka.connect.transforms.predicates.HasHeaderKey](#org.apache.kafka.connect.transforms.predicates.HasHeaderKey)

A predicate which is true for records with at least one header with the configured name.

* ###### [name](#org.apache.kafka.connect.transforms.predicates.HasHeaderKey_name)
    
    The header name.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: |     |
    | Valid Values: | non-empty string |
    | Importance: | medium |
    

##### [org.apache.kafka.connect.transforms.predicates.RecordIsTombstone](#org.apache.kafka.connect.transforms.predicates.RecordIsTombstone)

A predicate which is true for records which are tombstones (i.e. have null value).

##### [org.apache.kafka.connect.transforms.predicates.TopicNameMatches](#org.apache.kafka.connect.transforms.predicates.TopicNameMatches)

A predicate which is true for records with a topic name that matches the configured regular expression.

* ###### [pattern](#org.apache.kafka.connect.transforms.predicates.TopicNameMatches_pattern)
    
    A Java regular expression for matching against the name of a record's topic.
    
    |     |     |
    | --- | --- |
    | Type: | string |
    | Default: |     |
    | Valid Values: | non-empty string, valid regex |
    | Importance: | medium |
    

#### [REST API](#connect_rest)

Since Kafka Connect is intended to be run as a service, it also provides a REST API for managing connectors. The REST API server can be configured using the `listeners` configuration option. This field should contain a list of listeners in the following format: `protocol://host:port,protocol2://host2:port2`. Currently supported protocols are `http` and `https`. For example:

listeners=http://localhost:8080,https://localhost:8443

By default, if no `listeners` are specified, the REST server runs on port 8083 using the HTTP protocol. When using HTTPS, the configuration has to include the SSL configuration. By default, it will use the `ssl.*` settings. In case it is needed to use different configuration for the REST API than for connecting to Kafka brokers, the fields can be prefixed with `listeners.https`. When using the prefix, only the prefixed options will be used and the `ssl.*` options without the prefix will be ignored. Following fields can be used to configure HTTPS for the REST API:

* `ssl.keystore.location`
* `ssl.keystore.password`
* `ssl.keystore.type`
* `ssl.key.password`
* `ssl.truststore.location`
* `ssl.truststore.password`
* `ssl.truststore.type`
* `ssl.enabled.protocols`
* `ssl.provider`
* `ssl.protocol`
* `ssl.cipher.suites`
* `ssl.keymanager.algorithm`
* `ssl.secure.random.implementation`
* `ssl.trustmanager.algorithm`
* `ssl.endpoint.identification.algorithm`
* `ssl.client.auth`

The REST API is used not only by users to monitor / manage Kafka Connect. It is also used for the Kafka Connect cross-cluster communication. Requests received on the follower nodes REST API will be forwarded to the leader node REST API. In case the URI under which is given host reachable is different from the URI which it listens on, the configuration options `rest.advertised.host.name`, `rest.advertised.port` and `rest.advertised.listener` can be used to change the URI which will be used by the follower nodes to connect with the leader. When using both HTTP and HTTPS listeners, the `rest.advertised.listener` option can be also used to define which listener will be used for the cross-cluster communication. When using HTTPS for communication between nodes, the same `ssl.*` or `listeners.https` options will be used to configure the HTTPS client.

The following are the currently supported REST API endpoints:

* `GET /connectors` \- return a list of active connectors
* `POST /connectors` \- create a new connector; the request body should be a JSON object containing a string `name` field and an object `config` field with the connector configuration parameters
* `GET /connectors/{name}` \- get information about a specific connector
* `GET /connectors/{name}/config` \- get the configuration parameters for a specific connector
* `PUT /connectors/{name}/config` \- update the configuration parameters for a specific connector
* `GET /connectors/{name}/status` \- get current status of the connector, including if it is running, failed, paused, etc., which worker it is assigned to, error information if it has failed, and the state of all its tasks
* `GET /connectors/{name}/tasks` \- get a list of tasks currently running for a connector
* `GET /connectors/{name}/tasks/{taskid}/status` \- get current status of the task, including if it is running, failed, paused, etc., which worker it is assigned to, and error information if it has failed
* `PUT /connectors/{name}/pause` \- pause the connector and its tasks, which stops message processing until the connector is resumed
* `PUT /connectors/{name}/resume` \- resume a paused connector (or do nothing if the connector is not paused)
* `POST /connectors/{name}/restart?includeTasks=<true|false>&onlyFailed=<true|false>` \- restart a connector and its tasks instances.
    * the "includeTasks" parameter specifies whether to restart the connector instance and task instances ("includeTasks=true") or just the connector instance ("includeTasks=false"), with the default ("false") preserving the same behavior as earlier versions.
    * the "onlyFailed" parameter specifies whether to restart just the instances with a FAILED status ("onlyFailed=true") or all instances ("onlyFailed=false"), with the default ("false") preserving the same behavior as earlier versions.
* `POST /connectors/{name}/tasks/{taskId}/restart` \- restart an individual task (typically because it has failed)
* `DELETE /connectors/{name}` \- delete a connector, halting all tasks and deleting its configuration
* `GET /connectors/{name}/topics` \- get the set of topics that a specific connector is using since the connector was created or since a request to reset its set of active topics was issued
* `PUT /connectors/{name}/topics/reset` \- send a request to empty the set of active topics of a connector

Kafka Connect also provides a REST API for getting information about connector plugins:

* `GET /connector-plugins`\- return a list of connector plugins installed in the Kafka Connect cluster. Note that the API only checks for connectors on the worker that handles the request, which means you may see inconsistent results, especially during a rolling upgrade if you add new connector jars
* `PUT /connector-plugins/{connector-type}/config/validate` \- validate the provided configuration values against the configuration definition. This API performs per config validation, returns suggested values and error messages during validation.

The following is a supported REST request at the top-level (root) endpoint:

* `GET /`\- return basic information about the Kafka Connect cluster such as the version of the Connect worker that serves the REST request (including git commit ID of the source code) and the Kafka cluster ID that is connected to.

For the complete specification of the REST API, see the [OpenAPI documentation](/33/generated/connect_rest.yaml)

#### [Error Reporting in Connect](#connect_errorreporting)

Kafka Connect provides error reporting to handle errors encountered along various stages of processing. By default, any error encountered during conversion or within transformations will cause the connector to fail. Each connector configuration can also enable tolerating such errors by skipping them, optionally writing each error and the details of the failed operation and problematic record (with various levels of detail) to the Connect application log. These mechanisms also capture errors when a sink connector is processing the messages consumed from its Kafka topics, and all of the errors can be written to a configurable "dead letter queue" (DLQ) Kafka topic.

To report errors within a connector's converter, transforms, or within the sink connector itself to the log, set `errors.log.enable=true` in the connector configuration to log details of each error and problem record's topic, partition, and offset. For additional debugging purposes, set `errors.log.include.messages=true` to also log the problem record key, value, and headers to the log (note this may log sensitive information).

To report errors within a connector's converter, transforms, or within the sink connector itself to a dead letter queue topic, set `errors.deadletterqueue.topic.name`, and optionally `errors.deadletterqueue.context.headers.enable=true`.

By default connectors exhibit "fail fast" behavior immediately upon an error or exception. This is equivalent to adding the following configuration properties with their defaults to a connector configuration:

\# disable retries on failure
errors.retry.timeout=0

\# do not log the error and their contexts
errors.log.enable=false

\# do not record errors in a dead letter queue topic
errors.deadletterqueue.topic.name=

\# Fail on first error
errors.tolerance=none

These and other related connector configuration properties can be changed to provide different behavior. For example, the following configuration properties can be added to a connector configuration to setup error handling with multiple retries, logging to the application logs and the `my-connector-errors` Kafka topic, and tolerating all errors by reporting them rather than failing the connector task:

\# retry for at most 10 minutes times waiting up to 30 seconds between consecutive failures
errors.retry.timeout=600000
errors.retry.delay.max.ms=30000

\# log error context along with application logs, but do not include configs and messages
errors.log.enable=true
errors.log.include.messages=false

\# produce error context into the Kafka topic
errors.deadletterqueue.topic.name=my-connector-errors

\# Tolerate all errors.
errors.tolerance=all

### [8.3 Connector Development Guide](#connect_development)

This guide describes how developers can write new connectors for Kafka Connect to move data between Kafka and other systems. It briefly reviews a few key concepts and then describes how to create a simple connector.

#### [Core Concepts and APIs](#connect_concepts)

##### [Connectors and Tasks](#connect_connectorsandtasks)

To copy data between Kafka and another system, users create a `Connector` for the system they want to pull data from or push data to. Connectors come in two flavors: `SourceConnectors` import data from another system (e.g. `JDBCSourceConnector` would import a relational database into Kafka) and `SinkConnectors` export data (e.g. `HDFSSinkConnector` would export the contents of a Kafka topic to an HDFS file).

`Connectors` do not perform any data copying themselves: their configuration describes the data to be copied, and the `Connector` is responsible for breaking that job into a set of `Tasks` that can be distributed to workers. These `Tasks` also come in two corresponding flavors: `SourceTask` and `SinkTask`.

With an assignment in hand, each `Task` must copy its subset of the data to or from Kafka. In Kafka Connect, it should always be possible to frame these assignments as a set of input and output streams consisting of records with consistent schemas. Sometimes this mapping is obvious: each file in a set of log files can be considered a stream with each parsed line forming a record using the same schema and offsets stored as byte offsets in the file. In other cases it may require more effort to map to this model: a JDBC connector can map each table to a stream, but the offset is less clear. One possible mapping uses a timestamp column to generate queries incrementally returning new data, and the last queried timestamp can be used as the offset.

##### [Streams and Records](#connect_streamsandrecords)

Each stream should be a sequence of key-value records. Both the keys and values can have complex structure -- many primitive types are provided, but arrays, objects, and nested data structures can be represented as well. The runtime data format does not assume any particular serialization format; this conversion is handled internally by the framework.

In addition to the key and value, records (both those generated by sources and those delivered to sinks) have associated stream IDs and offsets. These are used by the framework to periodically commit the offsets of data that have been processed so that in the event of failures, processing can resume from the last committed offsets, avoiding unnecessary reprocessing and duplication of events.

##### [Dynamic Connectors](#connect_dynamicconnectors)

Not all jobs are static, so `Connector` implementations are also responsible for monitoring the external system for any changes that might require reconfiguration. For example, in the `JDBCSourceConnector` example, the `Connector` might assign a set of tables to each `Task`. When a new table is created, it must discover this so it can assign the new table to one of the `Tasks` by updating its configuration. When it notices a change that requires reconfiguration (or a change in the number of `Tasks`), it notifies the framework and the framework updates any corresponding `Tasks`.

#### [Developing a Simple Connector](#connect_developing)

Developing a connector only requires implementing two interfaces, the `Connector` and `Task`. A simple example is included with the source code for Kafka in the `file` package. This connector is meant for use in standalone mode and has implementations of a `SourceConnector`/`SourceTask` to read each line of a file and emit it as a record and a `SinkConnector`/`SinkTask` that writes each record to a file.

The rest of this section will walk through some code to demonstrate the key steps in creating a connector, but developers should also refer to the full example source code as many details are omitted for brevity.

##### [Connector Example](#connect_connectorexample)

We'll cover the `SourceConnector` as a simple example. `SinkConnector` implementations are very similar. Start by creating the class that inherits from `SourceConnector` and add a couple of fields that will store parsed configuration information (the filename to read from and the topic to send data to):

public class FileStreamSourceConnector extends SourceConnector {
    private String filename;
    private String topic;

The easiest method to fill in is `taskClass()`, which defines the class that should be instantiated in worker processes to actually read the data:

@Override
public Class&lt;? extends Task&gt; taskClass() {
    return FileStreamSourceTask.class;
}

We will define the `FileStreamSourceTask` class below. Next, we add some standard lifecycle methods, `start()` and `stop()`:

@Override
public void start(Map&lt;String, String&gt; props) {
    // The complete version includes error handling as well.
    filename = props.get(FILE_CONFIG);
    topic = props.get(TOPIC_CONFIG);
}

@Override
public void stop() {
    // Nothing to do since no background monitoring is required.
}

Finally, the real core of the implementation is in `taskConfigs()`. In this case we are only handling a single file, so even though we may be permitted to generate more tasks as per the `maxTasks` argument, we return a list with only one entry:

@Override
public List&lt;Map<String, String&gt;> taskConfigs(int maxTasks) {
    ArrayList&lt;Map<String, String&gt;> configs = new ArrayList<>();
    // Only one input stream makes sense.
    Map&lt;String, String&gt; config = new HashMap<>();
    if (filename != null)
        config.put(FILE_CONFIG, filename);
    config.put(TOPIC_CONFIG, topic);
    configs.add(config);
    return configs;
}

Although not used in the example, `SourceTask` also provides two APIs to commit offsets in the source system: `commit` and `commitRecord`. The APIs are provided for source systems which have an acknowledgement mechanism for messages. Overriding these methods allows the source connector to acknowledge messages in the source system, either in bulk or individually, once they have been written to Kafka. The `commit` API stores the offsets in the source system, up to the offsets that have been returned by `poll`. The implementation of this API should block until the commit is complete. The `commitRecord` API saves the offset in the source system for each `SourceRecord` after it is written to Kafka. As Kafka Connect will record offsets automatically, `SourceTask`s are not required to implement them. In cases where a connector does need to acknowledge messages in the source system, only one of the APIs is typically required.

Even with multiple tasks, this method implementation is usually pretty simple. It just has to determine the number of input tasks, which may require contacting the remote service it is pulling data from, and then divvy them up. Because some patterns for splitting work among tasks are so common, some utilities are provided in `ConnectorUtils` to simplify these cases.

Note that this simple example does not include dynamic input. See the discussion in the next section for how to trigger updates to task configs.

##### [Task Example - Source Task](#connect_taskexample)

Next we'll describe the implementation of the corresponding `SourceTask`. The implementation is short, but too long to cover completely in this guide. We'll use pseudo-code to describe most of the implementation, but you can refer to the source code for the full example.

Just as with the connector, we need to create a class inheriting from the appropriate base `Task` class. It also has some standard lifecycle methods:

public class FileStreamSourceTask extends SourceTask {
    String filename;
    InputStream stream;
    String topic;

    @Override
    public void start(Map&lt;String, String&gt; props) {
        filename = props.get(FileStreamSourceConnector.FILE_CONFIG);
        stream = openOrThrowError(filename);
        topic = props.get(FileStreamSourceConnector.TOPIC_CONFIG);
    }

    @Override
    public synchronized void stop() {
        stream.close();
    }

These are slightly simplified versions, but show that these methods should be relatively simple and the only work they should perform is allocating or freeing resources. There are two points to note about this implementation. First, the `start()` method does not yet handle resuming from a previous offset, which will be addressed in a later section. Second, the `stop()` method is synchronized. This will be necessary because `SourceTasks` are given a dedicated thread which they can block indefinitely, so they need to be stopped with a call from a different thread in the Worker.

Next, we implement the main functionality of the task, the `poll()` method which gets events from the input system and returns a `List<SourceRecord>`:

@Override
public List&lt;SourceRecord&gt; poll() throws InterruptedException {
    try {
        ArrayList&lt;SourceRecord&gt; records = new ArrayList<>();
        while (streamValid(stream) && records.isEmpty()) {
            LineAndOffset line = readToNextLine(stream);
            if (line != null) {
                Map&lt;String, Object&gt; sourcePartition = Collections.singletonMap("filename", filename);
                Map&lt;String, Object&gt; sourceOffset = Collections.singletonMap("position", streamOffset);
                records.add(new SourceRecord(sourcePartition, sourceOffset, topic, Schema.STRING_SCHEMA, line));
            } else {
                Thread.sleep(1);
            }
        }
        return records;
    } catch (IOException e) {
        // Underlying stream was killed, probably as a result of calling stop. Allow to return
        // null, and driving thread will handle any shutdown if necessary.
    }
    return null;
}

Again, we've omitted some details, but we can see the important steps: the `poll()` method is going to be called repeatedly, and for each call it will loop trying to read records from the file. For each line it reads, it also tracks the file offset. It uses this information to create an output `SourceRecord` with four pieces of information: the source partition (there is only one, the single file being read), source offset (byte offset in the file), output topic name, and output value (the line, and we include a schema indicating this value will always be a string). Other variants of the `SourceRecord` constructor can also include a specific output partition, a key, and headers.

Note that this implementation uses the normal Java `InputStream` interface and may sleep if data is not available. This is acceptable because Kafka Connect provides each task with a dedicated thread. While task implementations have to conform to the basic `poll()` interface, they have a lot of flexibility in how they are implemented. In this case, an NIO-based implementation would be more efficient, but this simple approach works, is quick to implement, and is compatible with older versions of Java.

##### [Sink Tasks](#connect_sinktasks)

The previous section described how to implement a simple `SourceTask`. Unlike `SourceConnector` and `SinkConnector`, `SourceTask` and `SinkTask` have very different interfaces because `SourceTask` uses a pull interface and `SinkTask` uses a push interface. Both share the common lifecycle methods, but the `SinkTask` interface is quite different:

public abstract class SinkTask implements Task {
    public void initialize(SinkTaskContext context) {
        this.context = context;
    }

    public abstract void put(Collection&lt;SinkRecord&gt; records);

    public void flush(Map&lt;TopicPartition, OffsetAndMetadata&gt; currentOffsets) {
    }

The `SinkTask` documentation contains full details, but this interface is nearly as simple as the `SourceTask`. The `put()` method should contain most of the implementation, accepting sets of `SinkRecords`, performing any required translation, and storing them in the destination system. This method does not need to ensure the data has been fully written to the destination system before returning. In fact, in many cases internal buffering will be useful so an entire batch of records can be sent at once, reducing the overhead of inserting events into the downstream data store. The `SinkRecords` contain essentially the same information as `SourceRecords`: Kafka topic, partition, offset, the event key and value, and optional headers.

The `flush()` method is used during the offset commit process, which allows tasks to recover from failures and resume from a safe point such that no events will be missed. The method should push any outstanding data to the destination system and then block until the write has been acknowledged. The `offsets` parameter can often be ignored, but is useful in some cases where implementations want to store offset information in the destination store to provide exactly-once delivery. For example, an HDFS connector could do this and use atomic move operations to make sure the `flush()` operation atomically commits the data and offsets to a final location in HDFS.

##### [Errant Record Reporter](connect_errantrecordreporter)

When [error reporting](#connect_errorreporting) is enabled for a connector, the connector can use an `ErrantRecordReporter` to report problems with individual records sent to a sink connector. The following example shows how a connector's `SinkTask` subclass might obtain and use the `ErrantRecordReporter`, safely handling a null reporter when the DLQ is not enabled or when the connector is installed in an older Connect runtime that doesn't have this reporter feature:

private ErrantRecordReporter reporter;

@Override
public void start(Map&lt;String, String&gt; props) {
    ...
    try {
        reporter = context.errantRecordReporter(); // may be null if DLQ not enabled
    } catch (NoSuchMethodException | NoClassDefFoundError e) {
        // Will occur in Connect runtimes earlier than 2.6
        reporter = null;
    }
}

@Override
public void put(Collection&lt;SinkRecord&gt; records) {
    for (SinkRecord record: records) {
        try {
            // attempt to process and send record to data sink
            process(record);
        } catch(Exception e) {
            if (reporter != null) {
                // Send errant record to error reporter
                reporter.report(record, e);
            } else {
                // There's no error reporter, so fail
                throw new ConnectException("Failed on record", e);
            }
        }
    }
}

##### [Resuming from Previous Offsets](#connect_resuming)

The `SourceTask` implementation included a stream ID (the input filename) and offset (position in the file) with each record. The framework uses this to commit offsets periodically so that in the case of a failure, the task can recover and minimize the number of events that are reprocessed and possibly duplicated (or to resume from the most recent offset if Kafka Connect was stopped gracefully, e.g. in standalone mode or due to a job reconfiguration). This commit process is completely automated by the framework, but only the connector knows how to seek back to the right position in the input stream to resume from that location.

To correctly resume upon startup, the task can use the `SourceContext` passed into its `initialize()` method to access the offset data. In `initialize()`, we would add a bit more code to read the offset (if it exists) and seek to that position:

stream = new FileInputStream(filename);
Map&lt;String, Object&gt; offset = context.offsetStorageReader().offset(Collections.singletonMap(FILENAME_FIELD, filename));
if (offset != null) {
    Long lastRecordedOffset = (Long) offset.get("position");
    if (lastRecordedOffset != null)
        seekToOffset(stream, lastRecordedOffset);
}

Of course, you might need to read many keys for each of the input streams. The `OffsetStorageReader` interface also allows you to issue bulk reads to efficiently load all offsets, then apply them by seeking each input stream to the appropriate position.

#### [Dynamic Input/Output Streams](#connect_dynamicio)

Kafka Connect is intended to define bulk data copying jobs, such as copying an entire database rather than creating many jobs to copy each table individually. One consequence of this design is that the set of input or output streams for a connector can vary over time.

Source connectors need to monitor the source system for changes, e.g. table additions/deletions in a database. When they pick up changes, they should notify the framework via the `ConnectorContext` object that reconfiguration is necessary. For example, in a `SourceConnector`:

if (inputsChanged())
    this.context.requestTaskReconfiguration();

The framework will promptly request new configuration information and update the tasks, allowing them to gracefully commit their progress before reconfiguring them. Note that in the `SourceConnector` this monitoring is currently left up to the connector implementation. If an extra thread is required to perform this monitoring, the connector must allocate it itself.

Ideally this code for monitoring changes would be isolated to the `Connector` and tasks would not need to worry about them. However, changes can also affect tasks, most commonly when one of their input streams is destroyed in the input system, e.g. if a table is dropped from a database. If the `Task` encounters the issue before the `Connector`, which will be common if the `Connector` needs to poll for changes, the `Task` will need to handle the subsequent error. Thankfully, this can usually be handled simply by catching and handling the appropriate exception.

`SinkConnectors` usually only have to handle the addition of streams, which may translate to new entries in their outputs (e.g., a new database table). The framework manages any changes to the Kafka input, such as when the set of input topics changes because of a regex subscription. `SinkTasks` should expect new input streams, which may require creating new resources in the downstream system, such as a new table in a database. The trickiest situation to handle in these cases may be conflicts between multiple `SinkTasks` seeing a new input stream for the first time and simultaneously trying to create the new resource. `SinkConnectors`, on the other hand, will generally require no special code for handling a dynamic set of streams.

#### [Connect Configuration Validation](#connect_configs)

Kafka Connect allows you to validate connector configurations before submitting a connector to be executed and can provide feedback about errors and recommended values. To take advantage of this, connector developers need to provide an implementation of `config()` to expose the configuration definition to the framework.

The following code in `FileStreamSourceConnector` defines the configuration and exposes it to the framework.

private static final ConfigDef CONFIG_DEF = new ConfigDef()
    .define(FILE_CONFIG, Type.STRING, Importance.HIGH, "Source filename.")
    .define(TOPIC_CONFIG, Type.STRING, Importance.HIGH, "The topic to publish data to");

public ConfigDef config() {
    return CONFIG_DEF;
}

`ConfigDef` class is used for specifying the set of expected configurations. For each configuration, you can specify the name, the type, the default value, the documentation, the group information, the order in the group, the width of the configuration value and the name suitable for display in the UI. Plus, you can provide special validation logic used for single configuration validation by overriding the `Validator` class. Moreover, as there may be dependencies between configurations, for example, the valid values and visibility of a configuration may change according to the values of other configurations. To handle this, `ConfigDef` allows you to specify the dependents of a configuration and to provide an implementation of `Recommender` to get valid values and set visibility of a configuration given the current configuration values.

Also, the `validate()` method in `Connector` provides a default validation implementation which returns a list of allowed configurations together with configuration errors and recommended values for each configuration. However, it does not use the recommended values for configuration validation. You may provide an override of the default implementation for customized configuration validation, which may use the recommended values.

#### [Working with Schemas](#connect_schemas)

The FileStream connectors are good examples because they are simple, but they also have trivially structured data -- each line is just a string. Almost all practical connectors will need schemas with more complex data formats.

To create more complex data, you'll need to work with the Kafka Connect `data` API. Most structured records will need to interact with two classes in addition to primitive types: `Schema` and `Struct`.

The API documentation provides a complete reference, but here is a simple example creating a `Schema` and `Struct`:

Schema schema = SchemaBuilder.struct().name(NAME)
    .field("name", Schema.STRING_SCHEMA)
    .field("age", Schema.INT_SCHEMA)
    .field("admin", SchemaBuilder.bool().defaultValue(false).build())
    .build();

Struct struct = new Struct(schema)
    .put("name", "Barbara Liskov")
    .put("age", 75);

If you are implementing a source connector, you'll need to decide when and how to create schemas. Where possible, you should avoid recomputing them as much as possible. For example, if your connector is guaranteed to have a fixed schema, create it statically and reuse a single instance.

However, many connectors will have dynamic schemas. One simple example of this is a database connector. Considering even just a single table, the schema will not be predefined for the entire connector (as it varies from table to table). But it also may not be fixed for a single table over the lifetime of the connector since the user may execute an `ALTER TABLE` command. The connector must be able to detect these changes and react appropriately.

Sink connectors are usually simpler because they are consuming data and therefore do not need to create schemas. However, they should take just as much care to validate that the schemas they receive have the expected format. When the schema does not match -- usually indicating the upstream producer is generating invalid data that cannot be correctly translated to the destination system -- sink connectors should throw an exception to indicate this error to the system.

#### [Kafka Connect Administration](#connect_administration)

Kafka Connect's [REST layer](#connect_rest) provides a set of APIs to enable administration of the cluster. This includes APIs to view the configuration of connectors and the status of their tasks, as well as to alter their current behavior (e.g. changing configuration and restarting tasks).

When a connector is first submitted to the cluster, a rebalance is triggered between the Connect workers in order to distribute the load that consists of the tasks of the new connector. This same rebalancing procedure is also used when connectors increase or decrease the number of tasks they require, when a connector's configuration is changed, or when a worker is added or removed from the group as part of an intentional upgrade of the Connect cluster or due to a failure.

In versions prior to 2.3.0, the Connect workers would rebalance the full set of connectors and their tasks in the cluster as a simple way to make sure that each worker has approximately the same amount of work. This behavior can be still enabled by setting `connect.protocol=eager`.

Starting with 2.3.0, Kafka Connect is using by default a protocol that performs [incremental cooperative rebalancing](https://cwiki.apache.org/confluence/display/KAFKA/KIP-415%3A+Incremental+Cooperative+Rebalancing+in+Kafka+Connect) that incrementally balances the connectors and tasks across the Connect workers, affecting only tasks that are new, to be removed, or need to move from one worker to another. Other tasks are not stopped and restarted during the rebalance, as they would have been with the old protocol.

If a Connect worker leaves the group, intentionally or due to a failure, Connect waits for `scheduled.rebalance.max.delay.ms` before triggering a rebalance. This delay defaults to five minutes (`300000ms`) to tolerate failures or upgrades of workers without immediately redistributing the load of a departing worker. If this worker returns within the configured delay, it gets its previously assigned tasks in full. However, this means that the tasks will remain unassigned until the time specified by `scheduled.rebalance.max.delay.ms` elapses. If a worker does not return within that time limit, Connect will reassign those tasks among the remaining workers in the Connect cluster.

The new Connect protocol is enabled when all the workers that form the Connect cluster are configured with `connect.protocol=compatible`, which is also the default value when this property is missing. Therefore, upgrading to the new Connect protocol happens automatically when all the workers upgrade to 2.3.0. A rolling upgrade of the Connect cluster will activate incremental cooperative rebalancing when the last worker joins on version 2.3.0.

You can use the REST API to view the current status of a connector and its tasks, including the ID of the worker to which each was assigned. For example, the `GET /connectors/file-source/status` request shows the status of a connector named `file-source`:

{
    "name": "file-source",
    "connector": {
        "state": "RUNNING",
        "worker_id": "192.168.1.208:8083"
    },
    "tasks": \[
        {
        "id": 0,
        "state": "RUNNING",
        "worker_id": "192.168.1.209:8083"
        }
    \]
}

Connectors and their tasks publish status updates to a shared topic (configured with `status.storage.topic`) which all workers in the cluster monitor. Because the workers consume this topic asynchronously, there is typically a (short) delay before a state change is visible through the status API. The following states are possible for a connector or one of its tasks:

* **UNASSIGNED:** The connector/task has not yet been assigned to a worker.
* **RUNNING:** The connector/task is running.
* **PAUSED:** The connector/task has been administratively paused.
* **FAILED:** The connector/task has failed (usually by raising an exception, which is reported in the status output).
* **RESTARTING:** The connector/task is either actively restarting or is expected to restart soon

In most cases, connector and task states will match, though they may be different for short periods of time when changes are occurring or if tasks have failed. For example, when a connector is first started, there may be a noticeable delay before the connector and its tasks have all transitioned to the RUNNING state. States will also diverge when tasks fail since Connect does not automatically restart failed tasks. To restart a connector/task manually, you can use the restart APIs listed above. Note that if you try to restart a task while a rebalance is taking place, Connect will return a 409 (Conflict) status code. You can retry after the rebalance completes, but it might not be necessary since rebalances effectively restart all the connectors and tasks in the cluster.

Starting with 2.5.0, Kafka Connect uses the `status.storage.topic` to also store information related to the topics that each connector is using. Connect Workers use these per-connector topic status updates to respond to requests to the REST endpoint `GET /connectors/{name}/topics` by returning the set of topic names that a connector is using. A request to the REST endpoint `PUT /connectors/{name}/topics/reset` resets the set of active topics for a connector and allows a new set to be populated, based on the connector's latest pattern of topic usage. Upon connector deletion, the set of the connector's active topics is also deleted. Topic tracking is enabled by default but can be disabled by setting `topic.tracking.enable=false`. If you want to disallow requests to reset the active topics of connectors during runtime, set the Worker property `topic.tracking.allow.reset=false`.

It's sometimes useful to temporarily stop the message processing of a connector. For example, if the remote system is undergoing maintenance, it would be preferable for source connectors to stop polling it for new data instead of filling logs with exception spam. For this use case, Connect offers a pause/resume API. While a source connector is paused, Connect will stop polling it for additional records. While a sink connector is paused, Connect will stop pushing new messages to it. The pause state is persistent, so even if you restart the cluster, the connector will not begin message processing again until the task has been resumed. Note that there may be a delay before all of a connector's tasks have transitioned to the PAUSED state since it may take time for them to finish whatever processing they were in the middle of when being paused. Additionally, failed tasks will not transition to the PAUSED state until they have been restarted.
