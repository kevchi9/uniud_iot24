## Architecture

![image](https://github.com/kevchi9/uniud_iot24/blob/main/resources/img/iot_project_schema.png)

## Raspberry modules

![rasp_components(1)](https://github.com/kevchi9/uniud_iot24/assets/62105685/3ba347d0-6faf-4569-96ca-5853a3b88b58)

- `Serial Port Reader(s)`: provided by the serial_port_reader.py file, which splits the workload on 3 different **threads**; each thread reads from a (virtual) serial port, then sends data on three dedicated pipes to the `Data Parser`;
- `Data Parser`: receives data on 3 pipes mentioned above, parses it, and forwards it on other 3 dedicated pipes to `Data Publisher`.
- `Data Publisher`: handles the connection to the **MQTT Broker**. Receives separated data on 3 pipes mentioned above, then publishes them on three different MQTT topics.

## Pipes
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



