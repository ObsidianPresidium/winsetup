import json
import sys
import os

class Optu:
    def __init__(self, locale="en", filename="main"):
        self.locale = locale
        self.filename = filename

        if getattr(sys, "frozen", False):
            root = sys._MEIPASS
        else:
            root = os.path.dirname(os.path.abspath(__file__))
        with open(f"{root}/optu/{locale}/{filename}.json", encoding="utf-8") as f:
            self.locale_dict = json.loads("".join(f.readlines()))

        self.locale_dict_string_as_id = {}
        for item in self.locale_dict:
            string_array = self.locale_dict[item]
            self.locale_dict_string_as_id.update({string_array[0]: [int(item), string_array[1]]})

    def get_string(self, string = None, id: int = -1, f: list = None):
        format_dict = {}
        format_list = f
        if format_list is not None:
            if len(format_list) > 8:
                errormsg = "Optu ERROR: Too many format specifiers!"
                print(errormsg)
                return errormsg
            format_specifiers = "stuvwxyz"
            for formatted_string in format_list:
                format_dict.update({"%" + format_specifiers[0]: formatted_string})
                format_specifiers = format_specifiers[1:]

        def format_string(formattee: str):
            if format_dict == {}:
                return formattee

            for key in format_dict:
                formattee = formattee.replace(key, str(format_dict[key]))
            return formattee

        if type(string) == int or id > -1:  # Search for string via ID lookup
            if type(string) == int: id = string
            id = str(id)
            to_return = self.locale_dict[id]
            return format_string(to_return[1])
        elif type(string) == str:
            try:
                return format_string(self.locale_dict_string_as_id[string][1])
            except KeyError:
                print(f"Optu WARNING: No string matching \"{string}\" was found. Using untranslated string")
                return format_string(string)
