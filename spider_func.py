import requests


def getHTMLText(url):
    try:
        new_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/65.0.3325.181 Safari/537.36'}
        old_headers = {'user-agent' : 'Mozilla/5.0'}
        r = requests.get(url, timeout=30, headers=new_headers)
        # print(r.status_code)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return 'DogError!'


# print(getHTMLText('https://www.bige7.com/book/1638/84.html'))
