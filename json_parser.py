import json


class JSONParser:
    def __init__(self, key_map: list[dict]):
        self.__key_map: list[dict] = key_map
        return

    def get_values(self, json_text: str) -> dict[str, str]:
        jd = json.loads(json_text)
        row: dict[str, str] = {}

        for i in range(len(self.__key_map)):
            last = jd
            path = self.__key_map[i]["path"]
            name = self.__key_map[i]["name"]
            for j in range(len(path)):
                key = path[j]
                if key.isdigit() and type(last) == list:
                    last = last[int(key)]
                elif key in last:
                    last = last[key]
                else:
                    print(f"json_parser: key_map improperly configured or provided bad json_text {last}")
            row[name] = last

        return row


def small_test():
    map_config = [
        {
            "name": "SuDoc",
            "path": [
                "classifications",
                "govDoc",
                "0"
            ]
        },
        {
            "name": "Title",
            "path": [
                "title",
                "mainTitles",
                "0"
            ]
        },
        {
            "name": "PublicationDate",
            "path": [
                "date",
                "publicationDate"
            ]
        }
    ]

    input_json = {
        "classifications": {
            "govDoc": [
                "DOCS 1:234/567"
            ]
        },
        "date": {
            "publicationDate": "1234"
        },
        "title": {
            "mainTitles": [
                "title_0"
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
