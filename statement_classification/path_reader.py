import sys
import re

class PathReader(object):
    def __init__(self, path_file):
        self.paths = {}
        for line in open(path_file):
            lnstrp = line.strip()
            if lnstrp.startswith('#'):
                continue
            key, value = re.split(' *= *', lnstrp)
            self.paths[key] = value
    def get_path(self, key):
        if key not in self.paths:
            raise KeyError, "Path to %s not set"%key
        return self.paths[key]
