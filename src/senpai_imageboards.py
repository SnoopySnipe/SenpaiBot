import requests

def yandere_get_latest_post():
    '''(void) -> dict


    '''

    # link for yande.re's json api
    api_url = "https://yande.re/post.json?limit=1"

    # get json contents
    web_content = requests.get(api_url)
    json_content = web_content.json()[0]

    return json_content

def danbooru_get_latest_post():

    api_url = "http://danbooru.donmai.us/posts.json?limit=1"

    # get json contents
    web_content = requests.get(api_url)
    json_content = web_content.json()[0]

    return json_content
