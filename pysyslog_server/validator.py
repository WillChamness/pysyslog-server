"""
Contains class to validate incoming Syslog messages. Invalid
messages are modified to adhere to the BSD Syslog format.
"""
import datetime
import re
from typing import Tuple, Pattern

class Validator():
    """
    Class for validating messages sent to the collector. 

    Although not strictly necessary according to RFC3164,
    Validation and correction is done for consistency in
    case the message did not reach a Syslog relay.

    Attributes:
        message (str): The original message sent to the collector.
        source_addr (str): The IP address of the client that sent the message.
        """

    def __init__(self, message: str, source_addr: str):
        """ 
        Inits Validator

        Args:
            message (str): The original message sent to the collector.
            source_addr (str): The IP address of the client that sent the message.
        """
        self.message = message
        self.source_addr = source_addr
        
    
    def validate_message(self) -> str:
        """
        Performs validation and correction of the message.

        Inserts a PRI and/or a HEADER depending on if the PRI
        and TIMESTAMP is valid or not.

        Returns:
            str: A valid (possibly corrected) syslog message.
        """
        if self._validate_pri():
            self._validate_timestamp()
        
        return self.message

            
    def _validate_pri(self) -> bool:
        """
        Validates the PRI as described in section 4.3. 

        If the PRI is invalid, prepend a valid PRI, a 
        TIMESTAMP, and a HOSTNAME to the message as described in 
        section 4.3.3. A default PRI value of 13 (facility == 1, 
        severity == 5) is added.

        Since the server doesn't know the hostname of the client,
        use the IP address instead as described by section 4.1.2.  

        Returns: 
            bool: Indicates whether or not the original message had
                a valid PRI
        """
        def prepend_pri_header():
            DEFAULT_PRI_VALUE: int = 13
            timestamp: str = str(datetime.datetime.now()).split(" ")
            date: str = timestamp[0].split("-")
            time: str = timestamp[1].split(".")
            months: list[str] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month: str = months[int(date[1]) - 1] # date is 1-based, but list is 0-based
            day: str = date[2] if int(date[2]) >= 10 else " " + str(int(date[2])) # replace leading 0 with space

            self.message = f"<{DEFAULT_PRI_VALUE}>{month} {day} {time[0]} {self.source_addr} {self.message}"

        pri_regex: Pattern = r"^<(191|190|1[0-8][0-9]|[1-9][0-9]|[0-9])>" # highest priority value is 191
        match_regex: bool = re.search(pri_regex, self.message)

        if not match_regex:
            prepend_pri_header()
            return False
        
        # check to make sure PRI isn't something like <0>> or <0>>>
        counter: int = 0
        seen_closing_bracket: bool = False
        while (not seen_closing_bracket) and counter < len("<191>"):
            if self.message[counter] == ">":
                seen_closing_bracket = True
            counter += 1

        while counter < len("<191>"):
            if self.message[counter] == ">":
                prepend_pri_header()
                return False
            counter += 1
        
        return True


    def _validate_timestamp(self):
        """
        Validates the format of the TIMESTAMP as described in section 4.1.2. 
        
        Assumes that the PRI has already been validated. 

        If timestamp is invalid, prepend the TIMESTAMP and HOSTNAME 
        to the HEADER as described in section 4.3.2 (creating a 
        new HEADER).

        Since the server doesn't know the client's hostname, use 
        the IP address instead as described in section 4.1.2.
        """
        # Mmm dd hh:mm:ss
        # if day < 10, first digit must be space
        timestamp_regex: Pattern = r"^.*>((Jan)|(Feb)|(Mar)|(Apr)|(May)|(Jun)|(Jul)|(Aug)|(Sep)|(Oct)|(Nov)|(Dec)) " \
            + r"(3[0-1]|[1-2][0-9]| [0-9]) (2[0-3]|[0-1][0-9]):[0-5][0-9]:[0-5][0-9] " 

        match_regex: bool = re.search(timestamp_regex, self.message)

        if not match_regex:
            timestamp: str = str(datetime.datetime.now()).split(" ")
            date: str = timestamp[0].split("-")
            time: str = timestamp[1].split(".")
            months: list[str] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month: str = months[int(date[1]) - 1] # date is 1-based, but list is 0-based
            day: str = date[2] if int(date[2]) >= 10 else " " + str(int(date[2])) # replace leading 0 with space

            counter: int = 0
            char: str = ""
            while char != ">":
                char = self.message[counter]
                counter += 1
            
            assert 3 <= counter and counter <= 5

            self.message = self.message[:counter] + f"{month} {day} {time[0]} {self.source_addr} " + self.message[counter:]