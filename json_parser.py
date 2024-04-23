import json


class JSONParser:
    def __init__(self, key_map: dict[str, list[str]]):
        self.__key_map: dict[str, list[str]] = key_map
        return

    def get_values(self, json_text: str) -> dict[str, str]:
        j = json.loads(json_text)
        row: dict[str, str] = {}

        last = j
        for col in self.__key_map:
            for i in range(len(self.__key_map[col])):
                key = self.__key_map[col][i]
                if key.isdigit() and type(last) == list:
                    last = last[int(key)]
                elif key in last:
                    last = last[key]
                else:
                    print("json_parser: key_map improperly configured or provided bad json_text")
            row[col] = last

        return row


def small_test():
    map_config = {
        "SuDoc": [
            "classifications",
            "govDoc",
            "0"
        ]
    }

    input_json = {
        "classifications": {
            "govDoc": [
                "DOCS 1:234/567"
            ]
        }
    }
    json_text = json.dumps(input_json)

    jp = JSONParser(map_config)
    row = jp.get_values(json_text)
    print(row)

    return


if __name__ == "__main__":
    small_test()
