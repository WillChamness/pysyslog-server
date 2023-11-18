"""Contains a class for parsing valid Syslog messages."""

import re
from typing import Tuple, Pattern

class Parser:
    """
    Class for parsing valid Syslog messages.

    Useful for splitting the message into facility, severity, date,
    time, hostname, tag, and content.

    Note that invalid messages may yield unexpected output.

    Attributes:
        syslog_message (str): The valid Syslog message to be parsed.
    """

    def __init__(self, syslog_message: str):
        """
        Inits Parser.

        Args: 
            syslog_message (str): The valid Syslog message to be parsed.
        """
        self.syslog_message = syslog_message

    
    def parse(self) -> dict:
        """
        Performs the parsing of the Syslog message.

        The result is the facility, severity, date, time, 
        hostname, tag, and content.

        Returns:
            dict: The results of the parsing. The keys are
                'facility', 'severity', etc.
        """
        ini, ini_stop_ind = self._parse_ini()
        date, time, timestamp_stop_ind = self._parse_timestamp(ini_stop_ind)
        hostname, hostname_stop_ind = self._parse_hostname(timestamp_stop_ind)
        tag, content = self._parse_tag_and_content(hostname_stop_ind)

        ini = ini[1:len(ini) - 1] # strip the angle brackets

        return {
            "facility": int(ini) // 8, 
            "severity": int(ini) % 8,
            "date": date,
            "time": time,
            "hostname": hostname,
            "tag": tag,
            "content": content
        }


    def _parse_ini(self) -> Tuple[str, int]:
        """
        Performs the parsing of the PRI part of the Syslog message.

        Since the message is valid by assumption, the PRI must end
        with the '>' character. The start of the message to this 
        character indicates the PRI.

        Returns:
            Tuple[str, int]: Contains the PRI (including angle brackets)
                and the index at which the TIMESTAMP begins.
        """
        char: str = ""
        counter: int = 0

        while char != ">":
            char = self.syslog_message[counter]
            counter += 1

        return (self.syslog_message[:counter], counter)

    
    def _parse_timestamp(self, start_ind: int) -> Tuple[str, str, int]:
        """
        Performs the parsing of the TIMESTAMP part of the Syslog message.

        Because the TIMESTAMP is always of the same form, the length of 
        the timestamp is always the same. The string is split, and 
        there are two cases to consider:

        Case 1 (dd >= 10):
            In this case, the result of the split is this array:
                ["Mmm", "dd", "hh:mm:ss"]
            The month, day, and time are simply the 0th, 1st, and  
            2nd items respectively.
        Case 2 (dd < 10):
            In this case, the result of the split is this array:
                ["Mmm", "", "d", "hh:mm:ss"]
            This is because the leading 0 in the day is replaced with a space.
            The month is the 0th item like in case 1, but the day and time
            are the 2nd and 3rd items respectively.

        Args:
            start_ind (int): The starting index of the TIMESTAMP.

        Returns:
            Tuple[str, str, int]: The month + day, time, and index at which
                the HOSTNAME begins
        """
        TIMESTAMP_LENGTH: int = len("Mmm dd hh:mm:ss")
        timestamp: str = self.syslog_message[start_ind : start_ind+TIMESTAMP_LENGTH].split(" ")
        month: str = timestamp[0]
        day: str = timestamp[1] if timestamp[1] else " " + timestamp[2] # if case 2, preserve additional space
        date: str = month + " " + day
        time: str = timestamp[2] if timestamp[1] else timestamp[3]

        return (date, time, start_ind + TIMESTAMP_LENGTH + 1) # don't include space at end


    def _parse_hostname(self, start_ind: int) -> Tuple[str, int]:
        """
        Performs the parsing of the HOSTNAME.

        Since the hostname depends on the Syslog device, the hostname
        is not checked. It is assumed that the device correctly 
        used its own DNS hostname or IP address.

        Because the message is valid by assumption, the HOSTNAME
        is terminated by a space character. 

        Args:
            start_ind (int): The starting index of the HOSTNAME.

        Returns:
            Tuple[str, int]: The HOSTNAME and index at which
                the TAG and CONTENT begin.
        """
        char: str = ""
        counter: int = start_ind

        while char != " ":
            char = self.syslog_message[counter]
            counter += 1

        hostname: str = self.syslog_message[start_ind : counter - 1] # don't include space

        return (hostname, counter)


    def _parse_tag_and_content(self, start_ind: int) -> Tuple[str, str]:
        """
        Performs the parsing of the TAG and CONTENT.

        There are no stipulations regarding TAG and CONTENT
        other than the TAG must be terminated by a non-alphanumeric
        character. When this character is met, the TAG ends and the
        CONTENT begins. All whitespace between the TAG and CONTENT 
        is preserved.

        Args:
            start_ind (int): The starting index of the TAG.
        
        Returns:
            Tuple[str, str]: The TAG and CONTENT.
        """
        MAX_TAG_LENGTH: int = 32
        char: str = "t"
        alphanumeric: Pattern = r"[a-z]|[A-Z]|[0-9]"
        alphanumeric_match: bool = re.search(alphanumeric, char)
        counter: int = start_ind

        while alphanumeric_match and counter - start_ind <= MAX_TAG_LENGTH:
            char = self.syslog_message[counter]
            counter += 1
            alphanumeric_match = re.search(alphanumeric, char)

        tag: str = self.syslog_message[start_ind:counter]
        content: str = self.syslog_message[counter:]

        return (tag, content)
        
