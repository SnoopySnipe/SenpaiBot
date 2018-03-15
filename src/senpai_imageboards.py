import requests

def yandere_get_latest_post():
    '''(void) -> dict


    '''

    # link for yande.re's json api
    api_url = "https://yande.re/post.json?limit=1"

    # get json contents
    json_content = requests.get(api_url).json()
    if (len(json_content) > 0):
        return json_content[0]

    return None

def danbooru_get_latest_post():

    api_url = "http://danbooru.donmai.us/posts.json?limit=1"

    # get json contents
    json_content = requests.get(api_url).json()
    if (len(json_content) > 0):
        return json_content[0]

    return None

def gelbooru_get_latest_post():

    api_url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=1"

    json_content = requests.get(api_url).json()
    if (len(json_content) > 0):
        return json_content[0]

    return None

def konachan_get_latest_post():
    '''(void) -> dict


    '''

    # link for konachan.com's json api
    api_url = "https://konachan.com/post.json?limit=1"

    # get json contents
    json_content = requests.get(api_url).json()
    if (len(json_content) > 0):
        return json_content[0]

    return None

if (__name__ == "__main__"):
    print("Yandere:")
    json_content = yandere_get_latest_post()
    print(json_content["id"])
    print(json_content["sample_url"])

    print("Danbooru:")
    json_content = danbooru_get_latest_post()
    print(json_content["id"])
    print(json_content["file_url"])

    print("Gelbooru")
    json_content = gelbooru_get_latest_post()
    print(json_content["id"])
    print(json_content["file_url"])


    print("Konachan:")
    json_content = konachan_get_latest_post()
    print(json_content["id"])
    print(json_content["sample_url"])


