import collections
import os


class DirDict(collections.MutableMapping):
    def __init__(self, path):
        if not os.path.exists(path):
            raise NotADirectoryError

        self.path = path
        self.all_files = []

    def __setitem__(self, key, value):
        self.all_files.append(key)
        with open(self.path + "/" + key, 'w') as file:
            file.write(value)

    def __getitem__(self, item):

        if not os.path.exists(self.path + "/" + item):
            raise KeyError

        with open(self.path + "/" + item, 'r') as file:
            value = file.read()
        return value

    def __delitem__(self, key):
        self.all_files.remove(key)
        if os.path.exists(self.path + "/" + key):
            os.remove(self.path + "/" + key)
        else:
            raise KeyError

    def __iter__(self):
        for file in self.all_files:
            yield self.__getitem__(file)

    def __len__(self):
        return len(self.all_files)
