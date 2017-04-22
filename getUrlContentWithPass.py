import requests
import re

def getUrlContentWithPass(url, password):
    cookie = 'BAIDUID=8D101D8173E6D75FF47A88DD65B29ACA:FG=1; PANWEB=1;'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Cookie': cookie,
        'Connection': 'keep-alive',
        'Referer': 'https://pan.baidu.com/'
    }
    
    f = requests.get(url, headers=headers, allow_redirects=False)
    #print(f.headers['Location'])
    initUrl = f.headers['Location']
    temp = initUrl.split('?')[1]
    dictUrl = {}
    for key_value in temp.split('&'):
        dictUrl[key_value.split('=')[0]] = key_value.split('=')[1]
    shareid = dictUrl['shareid']
    uk = dictUrl['uk']
    #print('%s %s' % (shareid, uk)) 

    veriUrl = 'https://pan.baidu.com/share/verify?shareid='+shareid+'&uk='+uk   
    data = {
        'pwd': password,
        'vcode': '',
        'vcode_str': ''
    }
    s = requests.Session()
    veriRes = s.post(veriUrl, headers=headers, data=data)
    
    cookie += 'BDCLND='+veriRes.cookies.get_dict()['BDCLND']+';'
    headers['Cookie'] = cookie
    linkUrl = 'https://pan.baidu.com/share/link?shareid='+shareid+'&uk='+uk
    
    linkRes = requests.get(linkUrl, headers=headers)
    linkRes.encoding = 'utf-8'
    
    result = {
        'BDCLND': veriRes.cookies.get_dict()['BDCLND'],
        'content': linkRes.text,
        'referer': 'http://pan.baidu.com/share/link?shareid='+shareid+'&uk='+uk
    }
    
    return result