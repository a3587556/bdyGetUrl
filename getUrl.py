from urllib import request
from urllib import parse
from getUrlContentWithPass import getUrlContentWithPass
import requests
import re
import json

def generateLink(content,url,cookie,sekey=None):
    if 'fs_id' in content:
        regex_fs_id = re.compile('"fs_id":([0-9]+)', re.S)
        fs_id = regex_fs_id.findall(content)
        regex_sign = re.compile('"sign":"([0-9a-z]+)"', re.S)
        sign = regex_sign.findall(content)
        regex_timestamp = re.compile('"timestamp":([0-9]+)', re.S)
        timestamp = regex_timestamp.findall(content)
        regex_uk = re.compile('"uk":([0-9]+)', re.S)
        uk = regex_uk.findall(content)
        regex_shareid = re.compile('"shareid":([0-9]+)', re.S)
        shareid = regex_shareid.findall(content)
        apiUrl = "https://pan.baidu.com/api/sharedownload?sign="+sign[0]+"&timestamp="+timestamp[0]
        headers = {
            "Referer": "https://pan.baidu.com/share/link?shareid="+shareid[0]+"&uk="+uk[0],
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/2008052906 Firefox/3.0",
            "X-Requested-With": "XMLHttpRequest"
        }
        data = {
            "encrypt": 0,
            "product": "share",
            "uk": uk[0],
            "primaryid": shareid[0],
            "fid_list": "["+fs_id[0]+"]"
        }
        if sekey is not None:
            data['extra'] = sekey
            
        params = parse.urlencode(data).encode(encoding='UTF8')
        req1 = request.Request(apiUrl, params, headers)
        result = request.urlopen(req1)
        contentJson = json.loads(result.read().decode('utf8'))
        dlink = contentJson['list'][0]['dlink']
        headers302 = {
            'Cookie': cookie,
            'Referer': url,
            'Host': 'd.pcs.baidu.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        res = requests.get(dlink, headers=headers302, allow_redirects=False)
        tempLink = res.headers['Location']
        hashLink = tempLink.split('file/')[1]
        link1 = 'http://nb.cache.baidupcs.com/file/'+hashLink
        link2 = 'http://pcs.dcdn.baidu.com/file/'+hashLink
        link3 = 'http://nb.poms.baidupcs.com/file/'+hashLink
        link4 = dlink
        link = {
            'link1': link1,
            'link2': link2,
            'link3': link3,
            'link4': link4
        }
        return link

def getUrl(panUrl, panPass=None):
    if panPass is None:
        url = panUrl
        cookie = 'BAIDUID=E1A86A79C89DFC76D38899822435B3D5:FG=1; PANWEB=1;'
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.1 Safari/537.11')
        req.add_header('Cookie', cookie)
        
        with request.urlopen(req) as f:
            content = f.read().decode('utf-8')
            return generateLink(content,url,cookie)
    else:
        result = getUrlContentWithPass(panUrl, panPass)
        content = result['content']
        linkUrl = result['referer']
        cookie = 'BAIDUID=E1A86A79C89DFC76D38899822435B3D5:FG=1; PANWEB=1; BDCLND='+result['BDCLND']
        sekey = json.dumps({"sekey": parse.unquote(result['BDCLND'])})
        return generateLink(content,linkUrl,cookie,sekey)
        

if __name__ == '__main__':
    getUrl("test")
