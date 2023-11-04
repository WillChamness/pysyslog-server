"""
Package that contains modules for collection, parsing,
and validation of Syslog messages.

The following environment variables need to be set
before using this package:
- SYSLOG_LISTEN_ADDRESS ('127.0.0.1' by default)
- SYSLOG_LISTEN_PORT ('514' by default)
- SYSLOG_FILE ('syslog.log' by default)
- SYSLOG_USE_DB ('no' by default)

If SYSLOG_USE_DB == "yes", then these additional 
environment variables need to be set (no defaults 
assigned):
- MONGODB_URI 
- MONGODB_DBNAME
- MONGODB_COLLECTION

See the 'python-dotenv' module for more information.

For convenience, you can begin the collector by
calling 'pysyslog_server.start()'. No need to import
'pysyslog_server.collector'. For example:

>>> import pysyslog_server
>>> pysyslog_server.start() # Listens for and handles Syslog messages

If you only want to validate individual messages, you can 
do so like this:

>>> from pysyslog_server.validator import Validator
>>> validator = Validator(message)
>>> valid_syslog_message = validator.validate()

If you only want to parse valid Syslog messages,
you can do so like this:

>>> from pysyslog_server.parser import Parser
>>> parser = Parser(valid_syslog_message)
>>> parsed_syslog = parser.parse()
"""
from .collector import start, handle_client