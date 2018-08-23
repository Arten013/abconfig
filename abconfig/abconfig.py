import configparser
import os

class ABConfig(object):
    CONF_ENCODERS = {}
    CONF_DECODERS = {}
    DEFAULT_SECTION = 'DEFAULT'
    def __init__(self):
        self.parser = configparser.ConfigParser(
                default_section = self.__class__.DEFAULT_SECTION
                )
        self.section_name = self.parser.default_section
        self._prev_section_name_stack = []
        self._exit_update_flag_stack = []

    @property
    def section(self):
        return self.parser[self.section_name]

    def get_default(self, key):
        with self.temporal_section_change(self.DEFAULT_SECTION):
            return self['default']

    def get(self, key, default):
        if key in self.section:
            return self[key]
        return default

    def link(self, path, create_if_missing=True):
        self.path = path
        if not os.path.exists(path):
            if create_if_missing:
                self.update_file()
            else:
                raise Exception(str(path)+' does not exist.')
        self.load()

    def is_linked(self):
        return self.path is not None

    def batch_update(self, name):
        self.load()
        self._prev_section_name_stack.append(self.section_name)
        self._exit_update_flag_stack.append(True)
        self.change_section(name)
        return self

    def temporal_section_change(self, name):
        self._prev_section_name_stack.append(self.section_name)
        self._exit_update_flag_stack.append(False)
        self.change_section(name)
        return self

    def __len__(self):
        return len(self.parser.sections())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            return False
        self._exit_update_flag_stack.pop() and self.update_file()
        self.section_name = self._prev_section_name_stack.pop()
        return True

    def has_section(self, name):
        return self.parser.has_section(name)

    def add_section(self, name):
        return self.parser.add_section(name)

    def change_section(self, name, create_if_missing=True):
        if name == self.DEFAULT_SECTION:
            self.section_name = name
            return
        if create_if_missing and not self.has_section(name):
            self.add_section(name)
        assert self.parser.has_section(name), 'There is no section named '+name+'.'
        self.section_name = name

    def load(self):
        if not self.is_linked():
            return
        with open(self.path) as f:
            self.parser.read_file(f)

    def update_file(self):
        if not self.is_linked:
            return
        os.makedirs(os.path.split(self.path)[0], exist_ok=True)
        with open(self.path, 'w') as f:
            self.parser.write(f, self)

    def iter_sections(self):
        for section_name in self.parser.sections():
            with self.temporal_section_change(section_name):
                yield section_name, self

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
                    'boltport': boltport
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

    @property
    def rest_loginkey(self):
        return {
                    'url': self.url,
                    'password': pw,
                    'username': usr

                }
