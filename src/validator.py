import datetime
import re

class Validator():
    """Class for validating messages sent to the collector. 
    Although not strictly necessary according to RFC3164,
    Validation and correction is done for consistency in
    case the message did not reach a Syslog relay.
    """
    def __init__(self, message, source_addr):
        self.message = message
        self.source_addr = source_addr
        
    
    def validate_message(self):
        """Driver for validation methods.
        """
        if self._validate_pri():
            self._validate_timestamp()
        
        return self.message

            
    def _validate_pri(self):
        """Validates the PRI as described in section 4.3. 

        If the PRI is invalid, prepend a valid PRI, a 
        TIMESTAMP, and a HOSTNAME to the message as described in 
        section 4.3.3.

        Since the server doesn't know the hostname of the client,
        use the IP address instead as described by section 4.1.2.  
        """
        pri_regex = r"^<(1[0-8][0-9]|[1-9][0-9]|[0-9])>" # highest priority value is 191
        match = re.search(pri_regex, self.message)

        
        if not match:
            timestamp = str(datetime.datetime.now()).split(" ")
            date = timestamp[0].split(" ")
            time = timestamp[1].split(".")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month = months[int(date[1])]
            day = date[2]

            self.message = f"<13>{month} {day} {time[0]} {self.source_addr} {self.message}"
            
            return False
        else:
            return True


    def _validate_timestamp(self):
        """Validates the format of the TIMESTAMP as described in
        section 4.1.2. Assumes that the PRI has already been
        validated. 

        If timestamp is invalid, prepend the TIMESTAMP and HOSTNAME 
        to the HEADER as described in section 4.3.2.

        Since the server doesn't know the client's hostname, use 
        the IP address instead as described in section 4.1.2.
        """
        # Mmm dd hh:mm:ss
        # if day < 10, first digit must be space
        timestamp_regex = r"^.*>((Jan)|(Feb)|(Mar)|(Apr)|(May)|(Jun)|(Jul)|(Aug)|(Sep)|(Oct)|(Nov)|(Dec)) " \
            + r"(3[0-1]|[1-2][0-9]| [0-9]) (2[0-3]|[0-1][0-9]):[0-5][0-9]:[0-5][0-9] " 

        match = re.search(timestamp_regex, self.message)

        if not match:
            timestamp = str(datetime.datetime.now()).split(" ")
            date = timestamp[0].split(" ")
            time = timestamp[1].split(".")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month = months[int(date[1])]
            day = date[2]

            counter = 0
            char = ""
            while char != ">":
                char = self.message[counter]
                counter += 1
            
            assert 3 <= counter and counter <= 5

            self.message = self.message[:counter] + f"{month} {day} {time[0]} {self.source_addr}" + self.message[counter:]