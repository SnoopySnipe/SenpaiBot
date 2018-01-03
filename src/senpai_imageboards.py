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

def gelbooru_get_latest_post():

    api_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=1"

    web_content = requests.get(api_url)
    json_content = web_content.json()[0]

    return json_content

def konachan_get_latest_post():
    '''(void) -> dict


    '''

    # link for konachan.com's json api
    api_url = "https://konachan.com/post.json?limit=1"

    # get json contents
    web_content = requests.get(api_url)
    json_content = web_content.json()[0]

    return json_content


