import os
import json
import math
import random
import requests
import threading
from urllib.parse import quote
from alive_progress import alive_bar
from urllib.request import urlretrieve

# 搜索关键字
keyword = ""
image_amount = 100
pagesize = 30
# image_num = 0

base_url = "https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&lm=7&fp=result&ie=utf-8&oe=utf-8&st=-1&word={}&queryWord={}&face=0&pn={}&rn={}"

headers = {
    'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50",
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

'''
1.构造图片搜索结果url列表
'''
def create_search_url_array():
    search_urls = []
    for i in range(math.ceil(image_amount / pagesize)):
        search_url = base_url.format(quote(keyword), quote(keyword), i * pagesize, pagesize)
        search_urls.append(search_url)
    # print(search_url)
    return search_urls

'''
2.批量访问搜索链接,返回json列表
'''
def get_from_search_urls(s, search_urls):
    res = []
    for search_url in search_urls:
        r = s.get(search_url, headers=headers)
        r.encoding = 'utf-8'
        response_json = json.loads(r.text.replace(r"\'", ""))
        res.append(response_json)
    return res

# '''
# 输出到文件以检查结果
# '''
# def output_debug_file(content):
#     with open('debug_res.txt', 'a', encoding='utf_8') as f:
#         f.write(content)

'''
4.解码url
'''
def decode_url(url):
        in_table, out_table = '0123456789abcdefghijklmnopqrstuvw', '7dgjmoru140852vsnkheb963wtqplifca'
        translate_table = str.maketrans(in_table, out_table)
        mapping = {'_z2C$q': ':', '_z&e3B': '.', 'AzdH3F': '/'}
        for k, v in mapping.items():
            url = url.replace(k, v)
        return url.translate(translate_table)

'''
3.获取下载地址
'''
def obtain_download_urls(response_jsons):
    res = []
    tmp = []
    for response_json in response_jsons:
        for item in response_json['data']:
            # print(item)
            if 'objURL' in item.keys():
                res.append(decode_url(item['objURL']))
        tmp.append(res)
    return tmp

'''
6.下载图片
'''
def download_images(urlset, bar):
    for url in urlset:
        image_num = random.randint(0, 10 * image_amount)
        urlretrieve(url,filename=r"./"+ keyword +"/"+ keyword + str(image_num) +".png")
        urlset.remove(url)
        bar()
# threads = []
# with alive_bar(len(urls)) as bar:
#     for _ in range(5):
#         task = threading.Thread(
#             target=download_images,
#             args=(urls, bar)
#         )
#         threads.append(task)
#         task.start()
#     for task in threads: task.join()

'''
5.创建多线程
'''
def multi_thread_download(urls):
    threads = []
    with alive_bar(len(urls)) as bar:
        for _ in range(5):
            task = threading.Thread(
                target=download_images,
                args=(urls, bar)
            )
            threads.append(task)
            task.start()
        for task in threads: task.join()

def main():
    os.makedirs('./'+ keyword +'/', exist_ok=True)
    session = requests.session()
    
    search_urls = create_search_url_array()
    response_jsons = get_from_search_urls(s=session, search_urls=search_urls)
    download_url_list = obtain_download_urls(response_jsons=response_jsons)
    # download_urls_set = parse_to_set(download_urls)

    for download_urls in download_url_list:
        download_set = set()
        for url in download_urls:
            download_set.add(url)
        multi_thread_download(download_set)

    # print(response_json['data'][0])
    # print(response_json)
    # output_debug_file(r.text)
    # print(r.text)

main()