import re
from typing import Tuple, Pattern

class Parser:
    def __init__(self, syslog_message: str):
        self.syslog_message = syslog_message

    
    def parse(self) -> str:
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
        char: str = ""
        counter: int = 0

        while char != ">":
            char = self.syslog_message[counter]
            counter += 1

        return (self.syslog_message[:counter], counter)

    
    def _parse_timestamp(self, start_ind: int) -> Tuple[str, str, int]:
        TIMESTAMP_LENGTH: int = len("Mmm dd hh:mm:ss")
        timestamp: str = self.syslog_message[start_ind : start_ind+TIMESTAMP_LENGTH].split(" ")
        month: str = timestamp[0]
        day: str = timestamp[1] if timestamp[1] else " " + timestamp[2]
        date: str = month + " " + day
        time: str = timestamp[2] if timestamp[1] else timestamp[3]

        return (date, time, start_ind + TIMESTAMP_LENGTH + 1) # don't include space


    def _parse_hostname(self, start_ind: int) -> Tuple[str, int]:
        char: str = ""
        counter: int = start_ind

        while char != " ":
            char = self.syslog_message[counter]
            counter += 1

        hostname: str = self.syslog_message[start_ind : counter - 1] # don't include space

        return (hostname, counter)


    def _parse_tag_and_content(self, start_ind: int) -> Tuple[str, str]:
        char: str = "t"
        alphanumeric: Pattern = r"[a-z]|[A-Z]|[0-9]"
        alphanumeric_match: bool = re.search(alphanumeric, char)
        counter: int = start_ind

        while alphanumeric_match and counter - start_ind <= 32:
            char = self.syslog_message[counter]
            counter += 1
            alphanumeric_match = re.search(alphanumeric, char)

        tag: str = self.syslog_message[start_ind:counter]
        content: str = self.syslog_message[counter:]

        return (tag, content)
        
