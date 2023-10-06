import re

class Parser:
    def __init__(self, syslog_message):
        self.string = syslog_message

    
    def parse(self):
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


    def _parse_ini(self):
        char = ""
        counter = 0

        while char != ">":
            char = self.string[counter]
            counter += 1

        return (self.string[:counter], counter)

    
    def _parse_timestamp(self, start_ind):
        TIMESTAMP_LENGTH = len("Mmm dd hh:mm:ss")
        timestamp = self.string[start_ind : start_ind+TIMESTAMP_LENGTH].split(" ")
        month = timestamp[0]
        day = timestamp[1] if timestamp[1] else " " + timestamp[2]
        date = month + " " + day
        time = timestamp[2] if timestamp[1] else timestamp[3]

        return (date, time, start_ind + TIMESTAMP_LENGTH + 1) # don't include space


    def _parse_hostname(self, start_ind):
        char = ""
        counter = start_ind

        while char != " ":
            char = self.string[counter]
            counter += 1

        hostname = self.string[start_ind : counter - 1] # don't include space

        return (hostname, counter)


    def _parse_tag_and_content(self, start_ind):
        char = "t"
        alphanumeric = r"[a-z]|[A-Z]|[0-9]"
        alphanumeric_match = re.search(alphanumeric, char)
        counter = start_ind

        while alphanumeric_match and counter - start_ind <= 32:
            char = self.string[counter]
            counter += 1
            alphanumeric_match = re.search(alphanumeric, char)

        tag = self.string[start_ind:counter]
        content = self.string[counter:]

        return (tag, content)
        
