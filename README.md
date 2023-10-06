# Syslog Server Implementation 
This project is a server-side implementation of the BSD Syslog Protocol ([RFC 3164](https://www.ietf.org/rfc/rfc3164.txt)) in Python.

# Syslog Overview
## Devices
Syslog clients, called "devices," send logging information about processes/applications for troubleshooting purposes. Naturally, this information is extremely valuable to engineers. For example, network engineers may find important information about routing protocols, interface changes, etc. in the Syslog messages for network devices. They are also able to prioritize critical errors over minor ones using Syslog's built-in priority indicator. They will know exactly when an error occurs because each Syslog message is timestamped. 

## Relays
Syslog relays exist to do two things: validate and correct incoming Syslog messages, and pass along Syslog messages to other relays and Syslog collectors. Syslog relays may keep some parts of the message and pass along the rest, acting as a collector. Although RFC 3164 doesn't specifically say so, relays presumably must forward part of the message. They will not keep the message without passing something to a relay/collector.

## Collector
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

# Installation
Ensure that Python, pip, venv, and Git are installed. Then, clone the repo with the following commands:
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

Lastly, send Syslog messages to the server on UDP/514 and watch as syslog file gets populated with entries.

**Note:** In Linux, the well-known ports require root privileges to open. Run `main.py` as root or use a reverse proxy.

# Auto Start After Reboot
This repo also contains an example `systemd` daemon file for starting the Syslog server after reboot. Modify `example-pysyslog-server.service` to fit your needs, and move it to `/etc/systemd/system/pysyslog-server.service`. Then, run these commands:
```
sudo systemctl enable pysyslog-server
sudo systemctl start pysyslog-server
```

Verify that the daemon is running correctly:
```
sudo systemctl status pysyslog-server
```

# Features
## Message Validation & Correction
As mentioned previously, collectors are not required to validate incoming messages. This is done by relays instead. However, this implementation performs the same validation/correction that relays would perform for the sake of consistency. As described by RFC 3164 section 4.3, the only parts that are validated are the PRI and the timestamp. The rest are assumed to be validated by the device. There are three cases to consider:

### Valid PRI and Timestamp
In this case, there is nothing to do. 

### Valid PRI, but Invalid Timestamp
In this case, a new HEADER is inserted immediately between the PRI and old HEADER. Although an invalid MSG may be created, the relay prioritizes quickly creating entries for humans rather than precise syntax. If the client wants to preserve the format of the message, it should adhere to the proper Syslog format.

### Invalid PRI
In this case, a new PRI and HEADER should be prepended to the message. Similar to before, this may result in an invalid MSG, but the priority is creating entries quickly.


# Todo
- Add Syslog web client
- Create docker images