import requests

def helloacm_get_fortune_cookie():

    api_url = "https://helloacm.com/api/fortune/"

    # get json contents
    json_content = requests.get(api_url).json()

    return json_content

if (__name__ == "__main__"):
    fortune = yerkee_get_fortune_cookie()
    print(fortune)
