from operator import itemgetter
from string import Template


class CaseTemplate(Template):
    delimiter = "@"


class SteroidDict:
    def __init__(self, dc=None):
        if dc is None:
            dc = {}
        self._dictionary = {}
        self._compute_dict = {}
        self._compute_dict_ordered_keys = []
        self.update(dc)

    def update(self, dc):
        for key, value in dc.items():
            self.__setitem__(key, value)

    def __getitem__(self, key):
        if (idx := self.function_key_index(key)) != -1:
            dc_copy = dict(self._dictionary)

            # compute all up to idx
            for k in self._compute_dict_ordered_keys[: idx + 1]:
                dc_copy[k] = self._compute_dict[k](dc_copy)

            return dc_copy[key]
        else:
            return self._dictionary[key]

    def function_key_index(self, key):
        try:
            return self._compute_dict_ordered_keys.index(key)
        except ValueError:
            return -1

    @staticmethod
    def is_iterable(value):
        return isinstance(value, tuple) or isinstance(value, list)

    # if the output of the function is iterable, return the i-th
    # item; else, return the item itself
    # also returns a boolean to check when this value was a list
    @classmethod
    def index_or_value(cls, value, index):
        if isinstance(value, list):
            if len(value) <= index:
                return (None, False)
            else:
                return (value[index], True)
        else:
            return (value, False)

    # we return a 2-tuple which tells if there is at least a list
    @classmethod
    def index_copy(cls, dictionary, index, up_to_key):
        # no function part
        ls = list(
            map(
                lambda v: SteroidDict.index_or_value(v, index),
                dictionary.values(),
            )
        )
        temp = list(zip(*ls))
        list_values = temp[0]
        # a list of booleans which tells which values was a list originally
        list_booleans = list(temp[1])

        dc = {}
        for key, value in zip(dictionary.keys(), list_values):
            if value is not None:
                dc[key] = value

        return (dc, any(list_booleans))

    # we support two types of templates: repeatable and non-repetable
    def set_computable_template(self, key, string, repetable=False):
        string_template = CaseTemplate(string)

        if repetable:

            def value(dc):
                strings = []
                i = 0
                try:
                    while True:
                        index_dc, a_list = SteroidDict.index_copy(dc, i, key)
                        strings.append(string_template.substitute(index_dc))

                        if a_list:
                            i += 1
                        else:
                            break
                except KeyError:
                    pass

                return "\n".join(strings)

        else:
            value = lambda dc: string_template.substitute(dc)

        self[key] = value

    def __setitem__(self, key, value):
        if callable(value):
            self._compute_dict[key] = value
            self._compute_dict_ordered_keys.append(key)
        else:
            self._dictionary[key] = value

    def items(self):
        dc = dict(self._dictionary)
        dc.update({key: self[key] for key in list(self._compute_dict.keys())})
        return dc

    def values(self):
        return self.items().values()

    def keys(self):
        ls = list(self._dictionary.keys())
        ls.extend(self._compute_dict.keys())
        return ls

    def __contains__(self, item):
        return item in self._dictionary or item in self._compute_dict

    def __delitem__(self, item):
        if item in self._dictionary:
            del self._dictionary[item]
        elif item in self._compute_dict:
            del self._compute_dict[item]
        else:
            raise ValueError("Deleting a non-existent object")
