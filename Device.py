class Device:
    def __init__(self, ip, name, config):
        self.ip = ip
        self.name = name
        self.config = config
        self.vlans = None

    def set_vlans(self, vlans):
        self.vlans = vlans
