from urllib import request
from urllib import parse
from getUrlContentWithPass import getUrlContentWithPass
from bs4 import BeautifulSoup
import pymongo
import requests
import re
import json
from postData import postData

def generateLink(url,cookie,outputlists,sekey=None,fileinfo=None):
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
        "fid_list": "["+str(fileinfo['fs_id'])+"]"
    }
    if sekey is not None:
        data['extra'] = sekey
    if fileinfo['isdir'] == 1:
        data['type'] = 'batch'

    params = parse.urlencode(data).encode(encoding='UTF8')
    req1 = request.Request(apiUrl, params, headers)
    result = request.urlopen(req1)
    contentJson = json.loads(result.read().decode('utf8'))
    dataDict = {}
    if fileinfo['isdir'] != 1:
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
            dataDict['dlink'] = tempLink
            dataDict['server_filename'] = fileinfo['server_filename']
            dataDict['isdir'] = 0
            outputlists.append(dataDict)
    else:
        dataDict['server_filename'] = '[文件夹] '+fileinfo['server_filename']
        dataDict['dlink'] = contentJson['dlink']+'&zipname=[文件夹]'+fileinfo['server_filename']+'.zip'
        dataDict['isdir'] = 1
        outputlists.append(dataDict)

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
            outputlists = []
            if ("yunData.FILEINFO =" in sourceData):
                regex_yundata_contents = re.compile('yunData\.FILEINFO = \[(.*?)\];', re.S)
                yundata_fileinfo_contents = regex_yundata_contents.findall(sourceData)
                yundata_fileinfo_lists_contents = yundata_fileinfo_contents[0].replace("},{","}|||{")
                yundata_fileinfo_lists = yundata_fileinfo_lists_contents.split("|||")
                for fileinfo_list in yundata_fileinfo_lists:
                    fileinfo_list_json = json.loads(fileinfo_list)
                    generateLink(url=url, cookie=cookie, outputlists=outputlists, fileinfo=fileinfo_list_json)
            else:
                regex_yundata_contents = re.compile('yunData.setData\((\{.*?\})\);', re.S)
                yundata_contents = regex_yundata_contents.findall(sourceData)
                fileinfo_list_json = json.loads(yundata_contents[0])['file_list']['list'][0]
                generateLink(url=url, cookie=cookie, outputlists=outputlists,fileinfo=fileinfo_list_json)
            return outputlists
    else:
        result = getUrlContentWithPass(panUrl, panPass)
        sourceData = result['content']
        linkUrl = result['referer']
        cookie = 'BAIDUID=E1A86A79C89DFC76D38899822435B3D5:FG=1; PANWEB=1; BDCLND='+result['BDCLND']
        sekey = json.dumps({"sekey": parse.unquote(result['BDCLND'])})
        getPostData(content=sourceData, postData=postData)
        outputlists = []
        if "yunData.FILEINFO =" in sourceData:
            regex_yundata_contents = re.compile('yunData\.FILEINFO = \[(.*?)\];', re.S)
            yundata_fileinfo_contents = regex_yundata_contents.findall(sourceData)
            yundata_fileinfo_lists_contents = yundata_fileinfo_contents[0].replace("},{", "}|||{")
            yundata_fileinfo_lists = yundata_fileinfo_lists_contents.split("|||")
            for fileinfo_list in yundata_fileinfo_lists:
                fileinfo_list_json = json.loads(fileinfo_list)
                generateLink(url=linkUrl, cookie=cookie, outputlists=outputlists,sekey=sekey, fileinfo=fileinfo_list_json)
        else:
            regex_yundata_contents = re.compile('yunData.setData\((\{.*?\})\);', re.S)
            yundata_contents = regex_yundata_contents.findall(sourceData)
            fileinfo_list_json = json.loads(yundata_contents[0])['file_list']['list'][0]
            generateLink(url=linkUrl, cookie=cookie, outputlists=outputlists, sekey=sekey, fileinfo=fileinfo_list_json)
        return outputlists

if __name__ == '__main__':
    getUrl("test")
