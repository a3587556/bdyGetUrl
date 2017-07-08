from urllib import request
from urllib import parse
from getUrlContentWithPass import getUrlContentWithPass
from bs4 import BeautifulSoup
import pymongo
import requests
import re
import json
from postData import postData

def generateLink(content,url,cookie,sekey=None):
    if 'fs_id' in content:
        apiUrl = "https://pan.baidu.com/api/sharedownload?sign="+postData.sign+"&timestamp="+postData.timestamp
        headers = {
            "Referer": "https://pan.baidu.com/share/link?shareid="+postData.shareid+"&uk="+postData.uk,
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/2008052906 Firefox/3.0",
            "X-Requested-With": "XMLHttpRequest"
        }
        data = {
            "encrypt": 0,
            "product": "share",
            "uk": postData.uk,
            "primaryid": postData.shareid,
            "fid_list": "["+postData.fs_id+"]"
        }
        if sekey is not None:
            data['extra'] = sekey
            
        params = parse.urlencode(data).encode(encoding='UTF8')
        req1 = request.Request(apiUrl, params, headers)
        result = request.urlopen(req1)
        contentJson = json.loads(result.read().decode('utf8'))
        lists = contentJson['list']
        for index,list in enumerate(lists):
            headers302 = {
                'Cookie': cookie,
                'Referer': url,
                'Host': 'd.pcs.baidu.com',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            res = requests.get(list['dlink'], headers=headers302, allow_redirects=False)
            tempLink = res.headers['Location']
            lists[index]['dlink'] = tempLink
        return lists

def getPostData(content, postData):
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

        postData.fs_id = fs_id[0]
        postData.sign = sign[0]
        postData.timestamp = timestamp[0]
        postData.shareid = shareid[0]
        postData.uk = uk[0]

def getUrl(panUrl, panPass=None):
    if panPass is None:
        url = panUrl
        cookie = 'BAIDUID=E1A86A79C89DFC76D38899822435B3D5:FG=1; PANWEB=1;'
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.1 Safari/537.11')
        req.add_header('Cookie', cookie)
        
        with request.urlopen(req) as f:
            content = f.read().decode('utf-8')
            soup = BeautifulSoup(content)
            sourceData = "".join(soup.select('script')[-1].contents)
            getPostData(content=sourceData,postData=postData)
            if ("yunData.FILEINFO =" in sourceData):
                regex_yundata_contents = re.compile('yunData\.FILEINFO = \[(.*?)\];', re.S)
                yundata_fileinfo_contents = regex_yundata_contents.findall(sourceData)
                regex_fid_lists = re.compile('"fs_id":([0-9]+)', re.S)
                fis_lists = regex_fid_lists.findall(yundata_fileinfo_contents[0])
                fis_lists_str = ",".join(fis_lists)
                postData.fs_id = fis_lists_str
            return generateLink(content=sourceData,url=url,cookie=cookie)
    else:
        result = getUrlContentWithPass(panUrl, panPass)
        content = result['content']
        linkUrl = result['referer']
        cookie = 'BAIDUID=E1A86A79C89DFC76D38899822435B3D5:FG=1; PANWEB=1; BDCLND='+result['BDCLND']
        sekey = json.dumps({"sekey": parse.unquote(result['BDCLND'])})
        getPostData(content=content, postData=postData)
        if ("yunData.FILEINFO =" in content):
            regex_yundata_contents = re.compile('yunData\.FILEINFO = \[(.*?)\];', re.S)
            yundata_fileinfo_contents = regex_yundata_contents.findall(content)
            regex_fid_lists = re.compile('"fs_id":([0-9]+)', re.S)
            fis_lists = regex_fid_lists.findall(yundata_fileinfo_contents[0])
            fis_lists_str = ",".join(fis_lists)
            postData.fs_id = fis_lists_str
        return generateLink(content,linkUrl,cookie,sekey)
        

if __name__ == '__main__':
    getUrl("test")
