import configparser
import os

class ABConfig(object):
    CONF_ENCODERS = {}
    CONF_DECODERS = {}
    def __init__(self, path=None):
        self.parser = configparser.ConfigParser()
        if path is not None:
            self.path = path
            os.path.exists(self.path) and self.load()
        self.section = self.parser['DEFAULT']

    def has_section(self, name):
        return self.parser.has_section(name)

    def change_section(self, name, create_if_missing=True):
        if create_if_missing:
            self.parser.add_section(name)
        assert self.parser.has_section(name), 'There is no section named '+name+'.'
        self.section = self.parser[name]

    def set_path(self, path):
        self.path = path

    def load(self):
        with open(self.path) as f:
            self.parser.read_file(f)

    def save(self):
        os.makedirs(os.path.split(self.path)[0], exist_ok=True)
        with open(self.path, 'w') as f:
            self.parser.write(f, self)

    def update(self):
        assert self.path is not None, 'You must set path before reload configure'
        self.save()
        self.load()

    def __getitem__(self, key):
        return self.CONF_DECODERS.get(key, str)(self.section[key])

    def __setitem__(self, key, value):
        self.section[key] = self.CONF_ENCODERS.get(key, str)(value)

class NEOConfig(ABConfig):
    def set_logininfo(self, host='localhost', port='17474', boltport='7687', usr='neo4j', pw='pass'):
        self.section.update(
                {
                    'port': str(port),
                    'usr': usr,
                    'pw': pw,
                    'host': host,
                }
            )

    @property
    def url(self):
        return 'http://{host}:{port}'.format(host=self.section['host'], port=self.section['port'])

    @property
    def bolturl(self):
        return 'bolt://{host}:{port}'.format(host=self.section['host'], port=self.section['boltport'])

    @property
    def loginkey(self):
        return {
                    'auth': (self.section['usr'], self.section['pw']),
                    'uri': self.bolturl
                }

