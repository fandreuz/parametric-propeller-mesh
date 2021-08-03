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
        self.update(dc)

    def update(self, dc):
        for key, value in dc.items():
            self.__setitem__(key, value)

    def __getitem__(self, key):
        if self.is_function(key):
            value = self._compute_dict[key]
            return value(self)
        else:
            return self._dictionary[key]

    def is_function(self, key):
        return key in self._compute_dict

    @staticmethod
    def is_iterable(value):
        return isinstance(value, tuple) or isinstance(value, list)

    # if the output of the function is iterable, return the i-th
    # item; else, return the item itself
    # also returns a boolean to check when this value was a list
    def index_or_value(self, key, index):
        value = self[key]
        if isinstance(value, list):
            return (value[index], True)
        else:
            return (value, False)

    # we return a 2-tuple which tells if there is at least a list
    def index_copy(self, index):
        # no function part
        nofunc_ls = [
            self.index_or_value(key, index) for key in self._dictionary.keys()
        ]
        temp = list(zip(*nofunc_ls))
        nofunc_list_values = temp[0]
        # a list of booleans which tells which values was a list originally
        list_booleans = list(temp[1])
        del temp

        dc = {
            key: value
            for key, value in zip(self._dictionary.keys(), nofunc_list_values)
        }

        # function part
        func_ls = [
            self.index_or_value(key, index)
            for key in list(self._compute_dict.keys())
        ]
        if(len(func_ls) > 0):
            temp = list(zip(*func_ls))
            func_list_values = temp[0]
            list_booleans.extend(temp[1])

            dc.update(
                {
                    key: value
                    for key, value in zip(self._compute_dict, func_list_values)
                }
            )
        return (dc,any(list_booleans))

    # we support two types of templates: repeatable and non-repetable
    def set_computable_template(self, key, string, repetable=False):
        string_template = CaseTemplate(string)

        if repetable:

            def value(dc):
                del dc._compute_dict[key]

                dc_index_copies = []
                try:
                    i = 0
                    while True:
                        index_dc, a_list = dc.index_copy(i)
                        dc_index_copies.append(index_dc)

                        if a_list:
                            i += 1
                        else:
                            break
                except IndexError:
                    pass
                dc[key] = value

                return "\n".join(
                    map(
                        lambda d: string_template.substitute(d),
                        dc_index_copies,
                    )
                )


        else:
            value = lambda dc: string_template.substitute(dc)

        self._compute_dict[key] = value

    def __setitem__(self, key, value):
        if callable(value):
            self._compute_dict[key] = value
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
