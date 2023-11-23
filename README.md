# Syslog Server Implementation 
This project is a server-side implementation of the BSD Syslog Protocol ([RFC 3164](https://www.ietf.org/rfc/rfc3164.txt)) in Python. See the [Syslog Overview](#bsd-syslog-overview) section for more information.

# Features
## Message Validation & Correction
Syslog collectors are not required to validate incoming messages. This is done by relays instead. However, this implementation performs the same validation/correction that relays would perform for the sake of consistency. 

## Docker Container Available
A Docker container is available [here](https://hub.docker.com/r/willchamness/pysyslog-server) for easy deployment. Instant logs everywhere! 

## Persistent Logs
If you're looking for a lightweight solution that doesn't involve a database, all messages are saved to a single file (`syslog.log` by default) in the `syslog/` directory. To get all logs from a specific device, use the `grep` command. For example:
```
grep /path/to/syslog/directory/syslog/syslog.log localhost
```

## Saving to a NoSQL Database
Although all logs are sent to a text file, they can also be sent to a MongoDB instance if configured. This database can be used to retrieve all messages or easily find messages from a specific device through a REST API, for example.

# Installation
## Docker
Make sure you have `docker` and `docker-compose` installed. To use the docker image, copy-paste the following lines into a `docker-compose.yml` file (using your own username/password):
```
version: '3.4'

services:
  syslog-server:
    image: willchamness/pysyslog-server:latest
    container_name: pysyslog-server
    restart: unless-stopped
    ports:
      - 514:514/udp
    environment:
      - SYSLOG_FILE=syslog.log
      - SYSLOG_LISTEN_ADDRESS=0.0.0.0
      - SYSLOG_LISTEN_PORT=514
      - SYSLOG_USE_DB=yes # if set to 'no', ignore mongodb configuration
      - MONGODB_URI=mongodb://mongoadmin:m0ngoadminPW!@mongo # username/password should be same as below
      - MONGODB_DBNAME=syslog
      - MONGODB_COLLECTION=logs
    volumes:
      - ./syslog:/app/syslog
    networks:
      - frontnet
      - backnet
    
  mongo:
    image: mongo:4.4  
    container_name: pysyslog-db
    restart: unless-stopped
    ports:
      - 27017:27017
    logging:
      options:
        max-size: 1g
    environment:  
      - MONGO_INITDB_ROOT_USERNAME=mongoadmin
      - MONGO_INITDB_ROOT_PASSWORD=m0ngoadminPW!
    volumes: 
      - ./mongodb-data:/data/db
    networks:
      - backnet

networks:
  frontnet:
    name: pysyslog_frontnet
  backnet:
    internal: true
    name: pysyslog_backnet
```

Then, run `docker-compose up -d` to run the server.

## Manual Installation
Ensure that Python 3.10+, pip, venv, and Git are installed. Then, clone the repo with the following commands:
```
git clone https://github.com/WillChamness/pysyslog-server
cd pysyslog-server
```

Then, create a virtual environment and activate it:
```
python -m venv env || python3 -m venv env
source env/bin/activate
```

Install dependencies and run the `main.py` file:
```
pip install -r requirements.txt || pip3 install -r requirements.txt
python main.py || python3 main.py
```

Next, create a `.env` file. Use the `.env_example` file a a template.

Lastly, send Syslog messages to the server on UDP/514 and watch as syslog file gets populated with entries. Check out [this Javascript Syslog client](https://github.com/paulgrove/node-syslog-client) to see if it works.

**Note:** In Linux, the well-known ports require root privileges to open. Run `main.py` as root or use a reverse proxy.

### Auto Start After Reboot
This repo also contains an example `systemd` daemon file for starting the Syslog server after reboot. Modify `example-pysyslog-server.service` to fit your needs and move it to `/etc/systemd/system/pysyslog-server.service`. Then, run these commands:
```
sudo systemctl enable pysyslog-server
sudo systemctl start pysyslog-server
```

Verify that the daemon is running correctly:
```
sudo systemctl status pysyslog-server
```

# BSD Syslog Overview
## Purpose
Logging data contains valuable information for technology-related fields. For software engineers, it is a useful tool for debugging applications. For IT administrators, it contains vital information to troubleshoot servers and network hardware. 

Although there are different varaints of Syslog, this project implements the BSD Syslog protocol. The full technical details can be found in [RFC 3164](https://www.ietf.org/rfc/rfc3164.txt).

## Devices
Syslog clients, called "devices," send logging information about processes/applications for troubleshooting purposes. As mentioned before, this information is extremely valuable to engineers. For example, network engineers may find important information about routing protocols, interface changes, etc. in the Syslog messages for network devices. They are also able to prioritize critical errors over minor ones using Syslog's built-in priority indicator. They will know exactly when an error occurs because each Syslog message is timestamped. 

## Relays
Syslog relays exist to do two things: validate and correct incoming Syslog messages, and pass along Syslog messages to other relays and Syslog collectors. Syslog relays may keep some parts of the message and pass along the rest, acting as a collector. Although RFC 3164 doesn't specifically say so, relays presumably must forward part of the message. They will not keep the message without passing something to a relay/collector.

## Collectors
Syslog servers, called "collectors," store valid Syslog messages for later use and are the focus of this repo. RFC 3164 does not mention anything about collectors validating incoming messages. This role is delegated to the relay. Furthermore, collectors must listen on UDP/514, and any traffic sent on this port is assumed to be Syslog data. The data sent must be 1024 bytes or less and encoded as ASCII characters. Also, RFC 3164 does not specify how the data should be stored. Syslog servers often save messages to a text file, but there is nothing stopping an implementor from saving to a database instead.

## Message Format
### PRI
The PRI is the very first part of the message. It is defined to be an opening angle bracket (<), a number indicating priority, and a closing angle bracket (>). The entire field is three, four, or five characters long. 

### HEADER
The HEADER immediately follows the PRI. It is defined as a timestamp followed by a hostname. The timestamp must be of the form "Mmm dd hh:mm:ss" (without the quotation marks). The timestamp and hostname are separated by a space, and the HEADER must end with a space.

The following restrictions are applied to the timestamp:
- Mmm must be Jan, Feb, Mar, etc.
- If dd is less than 10, then the first digit must be a space instead of 0
- hh must be between 0 and 23
- mm and ss must be between 0 and 59

The following restrictions are applied to the hostname:
- This field must be the device's hostname, IPv4 address, or IPv6 address
- The device's FQDN is not a valid hostname
- The device's hostname is preferred, but not required

### MSG
The MSG immediately follows the HEADER. It is defined as the tag followed by the content. The tag should represent the process/application that sent the message. It must be alphanumeric characters followed by a single non-alphanumeric character and cannot exceed 32 characters. By convention, the non-alphanumeric character is either a colon (":") or a left square bracket ("["). The content contains the details of the message and should describe the event to the reader.

### Example
RFC 3164 section 5.4 provides an example of a valid Syslog message:
```
<34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvickon /dev/pts/8
```

## Correcting Invalid Messages
Section 4.3 describes the following cases for relays to handle:

### Valid PRI and Timestamp
In this case, there is nothing to do. Log the message as normal.

### Valid PRI but Invalid Timestamp
In this case, a new HEADER must be inserted between the PRI and old timestamp. Then, log the result. Although this may result in an invalid MSG, the relay prioritizes creating entries for humans ***quickly*** over precise syntax. If the device wants the original message to be logged, it should adhere to the format of the Syslog message. 

### Invalid PRI
In this case, a new PRI and HEADER must be prepended to the original message. A default value of 13 is assigned as the priority value. Then, log the result. Again, this may result in an invalid MSG, but speed is prioritized.



# Todo
- Add Syslog web client
