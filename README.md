This software (still unnamed) is part of an IoT project for the university's IoT course.

The software is used (in our case on a Raspberry) to retrieve data from the central unit of a vehicle, a GPS and a gyroscope, parse the data, and send them to a cloud MQTT broker.

In our case, since the project has only learning purposes, all the data sources are emulated using actual data format standards.

The MQTT broker then sends the data through telegraf to influxDB (which is running on the same server).

On the same server Grafana is running and will query the DB to get and plot the data. A dashboard example is shown below.

The rest of the project (cloud server with MQTT broker and TIG stack) has nothing to do with this repository since it should be implemented by anyone who wants to deploy this.

## Architecture

![project_schema](https://github.com/kevchi9/uniud_iot24/assets/62105685/f29cf486-125a-453c-92ca-6ae365bf4f9a)

## Raspberry modules

![rasp_components(1)](https://github.com/kevchi9/uniud_iot24/assets/62105685/3ba347d0-6faf-4569-96ca-5853a3b88b58)

- `Serial Port Reader(s)`: provided by the serial_port_reader.py file, which splits the workload on 3 different **threads**; each thread reads from a (virtual) serial port, then sends data on three dedicated pipes to the `Data Parser`;
- `Data Parser`: receives data on 3 pipes mentioned above, parses it, and forwards it on other 3 dedicated pipes to `Data Publisher`.
- `Data Publisher`: handles the connection to the **MQTT Broker**. Receives separated data on 3 pipes mentioned above, then publishes them on three different MQTT topics.

### Pipes
The "pipes" used in the project are actually `multiprocess queues`, used to send and receive messages between processes. They work like a full duplex channels, but in this project are used as unidirectional pipes.

### MQTT Topics
Each topic receives data generated from a single data source (sensor).

The topics are the following (might change in the future):
- Kendau_GPS
- Control_Unit
- Gyroscope

## Logging

Logging is managed through the logging library. The used configuration can be found in the `logging.conf` file in the root directory.
For detailed info about the logging library follow the [official logging documentation](https://docs.python.org/3/library/logging.html).

## VPS modules

![VPS_architecture](https://github.com/kevchi9/uniud_iot24/assets/62105685/748ed722-3eb3-4f98-98c6-924eeeccebf6)

## Grafana Dashboard Example

![grafana](https://github.com/kevchi9/uniud_iot24/assets/62105685/995531de-f6a8-4728-97cd-714f3b955d72)
