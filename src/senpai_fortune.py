import requests

def yerkee_get_fortune_cookie():

    api_url = "http://www.yerkee.com/api/fortune"

    # get json contents
    json_content = requests.get(api_url).json()

    if "fortune" in json_content:
        return json_content["fortune"]

    return "Error: API down?"

if (__name__ == "__main__"):
    fortune = yerkee_get_fortune_cookie()
    print(fortune)
