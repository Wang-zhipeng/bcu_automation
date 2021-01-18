import yaml

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class XMLOperator:
    def __init__(self, file_path):
        self.tree = ET.parse(file_path)

    def get_root(self):
        return self.tree.getroot()

    def find_nodes(self, path):
        return self.tree.findall(path)

    @staticmethod
    def attrib(node):
        return node.attrib

    @staticmethod
    def tag(node):
        return node.tag

    def write(self, file_path):
        self.tree.write(file_path)

    @staticmethod
    def get_value(node, name):
        return node.attrib[name]

    @staticmethod
    def set_value(node, name, value):
        node.set(name, value)

    @staticmethod
    def iter(node):
        return node.iter()


class YamlOperator:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        with open(self.file_path, 'r') as f:
            result = yaml.safe_load(f)
        return result

    def write(self, content):
        with open(self.file_path, 'w')as f1:
            yaml.safe_dump(content, f1)


class TxtOperator:
    def __init__(self, filename, mode='a', encoding='utf8'):
        self._filename = filename
        self._mode = mode
        self._encoding = encoding

    def _get_read(self):
        return open(self._filename, 'r', encoding=self._encoding)

    def _get_write(self):
        return open(self._filename, 'w' if self._mode == 'w' else 'a', encoding=self._encoding)

    def get_lines(self):
        f = self._get_read()
        lines = f.readlines()
        f.close()
        return lines

    def get_source(self):
        f = self._get_read()
        source = f.read()
        f.close()
        return source

    def set_msg(self, msg):
        f = self._get_write()
        f.write(msg)
        f.close()

    def replace_msg(self, new, old):
        data = self.get_source()
        new_data = data.replace(old, new)
        self.set_msg(new_data)
