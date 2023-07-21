from bs4 import BeautifulSoup
import requests
import json
from http import HTTPStatus

username=''
password=''

def get_auth_token(username,password):
    client = requests.Session()
    client.headers.update(
        {
             "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
        }
    )

    # Fetch the login page to get the csrf_token
    r = client.get("https://www.reddit.com/login")
    login_get_soup = BeautifulSoup(r.content, "html.parser")
    csrf_token = login_get_soup.find("input", {"name": "csrf_token"})["value"]

    data = {
        "username": username,
        "password": password,
        "csrf_token": csrf_token,
    }
    print(r.text)
    # Post the login credentials to get the token
    r = client.post("https://www.reddit.com/login", data=data)
    print(r.text)
    if r.status_code != HTTPStatus.OK.value:
        r = client.get("https://new.reddit.com/")
        data_str = (
            BeautifulSoup(r.content, features="html.parser")
            .find("script", {"id": "data"})
            .contents[0][len("window.__r = ") : -1]
        )
        data = json.loads(data_str)
        response_data = data["user"]["session"]

        token = response_data.get("accessToken") or response_data.get("refreshToken")
        return token

    return None

access_token_in = get_auth_token(username,password)

def place_pixel(x, y, color_index_in, canvas_index, access_token_in):
    url = "https://gql.reddit.com/query"
    payload = json.dumps(
        {
            "operationName": "setPixel",
            "variables": {
                "input": {
                    "actionName": "place_pixel",
                    "canvasId": canvas_index,
                    "PixelMessageData": {
                        "coordinate": {"x": x, "y": y},
                        "colorIndex": color_index_in,
                    },
                }
            },
            "query": "mutation setPixel($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetUserCooldownResponseMessageData {\n            nextAvailablePixelTimestamp\n            __typename\n          }\n          ... on SetPixelResponseMessageData {\n            timestamp\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
        }
    )
    headers = {
        "origin": "https://www.reddit.com",
        "referer": "https://www.reddit.com/",
        "apollographql-client-name": "reddit",
        "Authorization": "Bearer " + access_token_in,
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

# Example usage

place_pixel(471, 469, 4, 2, access_token_in)