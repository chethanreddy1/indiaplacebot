
import requests
from requests import Session, auth
from json import loads, dump
from stem import Signal
from stem.control import Controller
from random import choice
import jwt
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType


def accest(username,password):

    options = Options()
    options.add_argument('--headless')  
    driver = webdriver.Chrome(options=options)

    login_url = 'https://www.reddit.com/login'
    driver.get(login_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'loginUsername')))

    username_input = driver.find_element(By.ID, 'loginUsername')
    password_input = driver.find_element(By.ID, 'loginPassword')
    username_input.send_keys(username)
    password_input.send_keys(password)


    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(3)

    javascript_code = """
    const getAccessToken = async () => {
        console.log("Called");
        const usingOldReddit = window.location.href.includes('new.reddit.com');
        const url = usingOldReddit ? 'https://new.reddit.com/r/place/' : 'https://www.reddit.com/r/place/';
        const response = await fetch(url);
        const responseText = await response.text();

        return responseText.match(/"accessToken":"(\\"|[^"]*)"/)[1];
    };

    return getAccessToken();
    """


    access_token = driver.execute_script(javascript_code)
    return access_token

def getCanvasId(x, y):
    if y < 0 and x < -500:
        return 0
    elif y < 0 and -500 <= x < 500:
        return 1
    elif y < 0 and x >= 500:
        return 2
    elif y >= 0 and x < -500:
        return 3
    elif y >= 0 and -500 <= x < 500:
        return 4
    elif y >= 0 and x >= 500:
        return 5


def getCanvasX(x, y):
    return abs((x + 500) % 1000)

def getCanvasY(x, y):
    if y<0 :
        return y + 1000
    else:
        return y
    

def setpixel_payload(coordinates, color):
    x, y = coordinates
    return {'operationName': 'setPixel',
            'query': "mutation setPixel($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetUserCooldownResponseMessageData {\n            nextAvailablePixelTimestamp\n            __typename\n          }\n          ... on SetPixelResponseMessageData {\n            timestamp\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
            'variables': {
                'input': {
                    'PixelMessageData': {'coordinate': {'x': getCanvasX(x,y) , 'y': getCanvasY(x,y)}, 'colorIndex': color, 'canvasIndex': getCanvasId(x,y)},
                    'actionName': "r/replace:set_pixel"
                }
            }
            }



def set_pixel(acces,coordinates, color):
    print(acces)
    session=Session()
    r = session.post('https://gql-realtime-2.reddit.com/query', headers={'content-type': 'application/json',
                                                                            'origin': "https://garlic-bread.reddit.com",
                                                                            'referer': "https://garlic-bread.reddit.com/",
                                                                            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
                                                                            'apollographql-client-name': "garlic-bread",
                                                                            'apollographql-client-version': '0.0.1',
                                                                            'authorization': f'Bearer {acces}'}, json= setpixel_payload(coordinates, color))
    return r.text

a=accest(username,password)
set_pixel(a,(426, -238), 6)