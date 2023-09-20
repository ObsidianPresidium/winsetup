import json

class Optu:
    def __init__(self, locale="en", filename="main"):
        self.locale = locale
        self.filename = filename
        with open(f"optu/{locale}/{filename}.json", encoding="utf-8") as f:
            self.locale_dict = json.loads("".join(f.readlines()))

        self.locale_dict_string_as_id = {}
        for item in self.locale_dict:
            string_array = self.locale_dict[item]
            self.locale_dict_string_as_id.update({string_array[0]: [int(item), string_array[1]]})

    def get_string(self, string=None, id=-1):
        if type(string) == int or id > -1:  # Search for string via ID lookup
            if type(string) == int: id = string
            id = str(id)
            to_return = self.locale_dict[id]
            return to_return[1]
        elif type(string) == str:
            return self.locale_dict_string_as_id[string][1]