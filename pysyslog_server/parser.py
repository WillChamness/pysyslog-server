class Parser:
    def __init__(self, syslog_message):
        self.string = syslog_message

    
    def parse(self):
        raise NotImplementedError("Parsing not yet implemented")