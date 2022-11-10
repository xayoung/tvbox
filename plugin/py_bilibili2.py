#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import time
import base64

class Spider(Spider):  # 元类 默认的元类 type
    def getName(self):
        return "哔哩哔哩"
    def init(self,extend=""):
        print("============{0}============".format(extend))
        pass
    def isVideoFormat(self,url):
        pass
    def manualVideoCheck(self):
        pass
    def homeContent(self,filter):
        result = {}
        cateManual = {
            "动态":"动态",
            "热门":"热门",
            "排行榜":"排行榜",
            "番剧": "1",
			"国创": "4",
			"电影": "2",
			"综艺": "7",
			"电视剧": "5",
			"纪录片": "3"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name':k,
                'type_id':cateManual[k]
            })
        result['class'] = classes
        if(filter):
            result['filters'] = self.config['filter']
        return result
    def homeVideoContent(self):
        result = {
            'list':[]
        }
        return result
    cookies = ''
    def getCookie(self):
        import requests
        import http.cookies
        raw_cookie_line = "buvid3=F87F0A11-46CF-848D-6DFF-E8A6FF7060A766081infoc; rpdid=|(J|~ukYY|~)0J'uYYY~lYYY~; buvid_fp=F87F0A11-46CF-848D-6DFF-E8A6FF7060A766081infoc; buvid_fp_plain=undefined; DedeUserID=131773; DedeUserID__ckMd5=54f906a0afc0ce2c; i-wanna-go-back=-1; b_ut=5; nostalgia_conf=-1; hit-dyn-v2=1; buvid4=null; b_nut=1667183288; fingerprint=c1b65158bb87079465a8da1e534826d0; CURRENT_QUALITY=0; blackside_state=1; bp_video_offset_131773=723849023477252100; CURRENT_FNVAL=16; innersign=0; SESSDATA=378de8a5,1683528686,11a4d*b2; bili_jct=cb8b96e31d5300c2d4412b4415a54182; sid=ojy6c7g8"
        simple_cookie = http.cookies.SimpleCookie(raw_cookie_line)
        cookie_jar = requests.cookies.RequestsCookieJar()
        cookie_jar.update(simple_cookie)
        return cookie_jar
    def get_dynamic(self,pg):
        result = {}
        if int(pg) > 1:
            return result
        offset = ''
        videos = []
        for i in range(0,10):
            url= 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all?timezone_offset=-480&type=all&page={0}&offset={1}'.format(pg,offset)
            rsp = self.fetch(url,cookies=self.getCookie())
            content = rsp.text
            jo = json.loads(content)
            if jo['code'] == 0:
                offset = jo['data']['offset']
                vodList = jo['data']['items']
                for vod in vodList:
                    if vod['type'] == 'DYNAMIC_TYPE_AV':
                        ivod = vod['modules']['module_dynamic']['major']['archive']
                        aid = str(ivod['aid']).strip()
                        title = ivod['title'].strip().replace("<em class=\"keyword\">","").replace("</em>","")
                        img =  ivod['cover'].strip()
                        remark = str(ivod['duration_text']).strip()
                        videos.append({
                            "vod_id":aid,
                            "vod_name":title,
                            "vod_pic":img,
                            "vod_remarks":remark
                        })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result
    def get_hot(self,pg):
        result = {}
        url= 'https://api.bilibili.com/x/web-interface/popular?ps=20&pn={0}'.format(pg)
        rsp = self.fetch(url,cookies=self.getCookie())
        content = rsp.text
        jo = json.loads(content)
        if jo['code'] == 0:
            videos = []
            vodList = jo['data']['list']
            for vod in vodList:
                aid = str(vod['aid']).strip()
                title = vod['title'].strip().replace("<em class=\"keyword\">","").replace("</em>","")
                img =  vod['pic'].strip()
                remark = str(vod['duration']).strip()
                videos.append({
                    "vod_id":aid,
                    "vod_name":title,
                    "vod_pic":img,
                    "vod_remarks":remark
                })
            result['list'] = videos
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 90
            result['total'] = 999999
        return result
    def get_rank(self):
        result = {}
        url= 'https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all'
        rsp = self.fetch(url,cookies=self.getCookie())
        content = rsp.text
        jo = json.loads(content)
        if jo['code'] == 0:
            videos = []
            vodList = jo['data']['list']
            for vod in vodList:
                aid = str(vod['aid']).strip()
                title = vod['title'].strip().replace("<em class=\"keyword\">","").replace("</em>","")
                img =  vod['pic'].strip()
                remark = str(vod['duration']).strip()
                videos.append({
                    "vod_id":aid,
                    "vod_name":title,
                    "vod_pic":img,
                    "vod_remarks":remark
                })
            result['list'] = videos
            result['page'] = 1
            result['pagecount'] = 1
            result['limit'] = 90
            result['total'] = 999999
        return result
    def categoryContent(self,tid,pg,filter,extend):	
        result = {}
        if tid == "热门":
            return self.get_hot(pg=pg)
        if tid == "排行榜" :
            return self.get_rank()
        if tid == '动态':
            return self.get_dynamic(pg=pg)
        url = 'https://api.bilibili.com/pgc/season/index/result?order=2&season_status=-1&style_id=-1&sort=0&area=-1&pagesize=20&type=1&st={0}&season_type={0}&page={1}'.format(tid,pg)
        if len(self.cookies) <= 0:
            self.getCookie()
        rsp = self.fetch(url, cookies=self.cookies)
        content = rsp.text
        jo = json.loads(content)
        videos = []
        vodList = jo['data']['list']
        for vod in vodList:
            aid = str(vod['season_id']).strip()
            title = vod['title'].strip()
            img =  vod['cover'].strip()
            remark = vod['index_show'].strip()
            videos.append({
				"vod_id":aid,
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":remark,
				"type":1
			})
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result
    def cleanSpace(self,str):
        return str.replace('\n','').replace('\t','').replace('\r','').replace(' ','')
    def detailContent(self,array):
        aid = array[0]
        type = array[4]
        if type :
            url = "http://api.bilibili.com/pgc/view/web/season?season_id={0}".format(aid)
            rsp = self.fetch(url,headers=self.header)
            jRoot = json.loads(rsp.text)
            jo = jRoot['result']
            id = jo['season_id']
            title = jo['title']
            pic = jo['cover']
            areas = jo['areas'][0]['name']
            typeName = jo['share_sub_title']
            dec = jo['evaluate']
            remark = jo['new_ep']['desc']
            vod = {
                "vod_id":id,
                "vod_name":title,
                "vod_pic":pic,
                "type_name":typeName,
                "vod_year":"",
                "vod_area":areas,
                "vod_remarks":remark,
                "vod_actor":"",
                "vod_director":"",
                "vod_content":dec
            }
            ja = jo['episodes']
            playUrl = ''
            for tmpJo in ja:
                eid = tmpJo['id']
                cid = tmpJo['cid']
                part = tmpJo['title'].replace("#", "-")
                playUrl = playUrl + '{0}${1}_{2}#'.format(part, eid, cid)

            vod['vod_play_from'] = 'B站影视'
            vod['vod_play_url'] = playUrl

            result = {
                'list':[
                    vod
                ]
            }
            return result
        else:
            url = "https://api.bilibili.com/x/web-interface/view?aid={0}".format(aid)
            rsp = self.fetch(url,headers=self.header,cookies=self.getCookie())
            jRoot = json.loads(rsp.text)
            jo = jRoot['data']
            title = jo['title'].replace("<em class=\"keyword\">","").replace("</em>","")
            pic = jo['pic']
            desc = jo['desc']
            typeName = jo['tname']
            vod = {
                "vod_id":aid,
                "vod_name":title,
                "vod_pic":pic,
                "type_name":typeName,
                "vod_year":"",
                "vod_area":"bilidanmu",
                "vod_remarks":"",
                "vod_actor":jo['owner']['name'],
                "vod_director":jo['owner']['name'],
                "vod_content":desc
            }
            ja = jo['pages']
            playUrl = ''
            for tmpJo in ja:
                cid = tmpJo['cid']
                part = tmpJo['part']
                playUrl = playUrl + '{0}${1}_{2}#'.format(part,aid,cid)

            vod['vod_play_from'] = 'B站'
            vod['vod_play_url'] = playUrl

            result = {
                'list':[
                    vod
                ]
            }
            return result
    def searchContent(self,key,quick):
        search = self.categoryContent(tid=key,pg=1,filter=None,extend=None)
        result = {
            'list':search['list']
        }
        return result
    def playerContent(self,flag,id,vipFlags):
        # https://www.555dianying.cc/vodplay/static/js/playerconfig.js
        result = {}

        ids = id.split("_")
        url = 'https://api.bilibili.com:443/x/player/playurl?avid={0}&cid=%20%20{1}&qn=112'.format(ids[0],ids[1])
        rsp = self.fetch(url,cookies=self.getCookie())
        jRoot = json.loads(rsp.text)
        jo = jRoot['data']
        ja = jo['durl']
        
        maxSize = -1
        position = -1
        for i in range(len(ja)):
            tmpJo = ja[i]
            if maxSize < int(tmpJo['size']):
                maxSize = int(tmpJo['size'])
                position = i

        url = ''
        if len(ja) > 0:
            if position == -1:
                position = 0
            url = ja[position]['url']

        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = url
        result["header"] = {
            "Referer":"https://www.bilibili.com",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        result["contentType"] = 'video/x-flv'
        return result

    config = {
        "player": {},
        "filter": {}
    }
    header = {}

    def localProxy(self,param):
        return [200, "video/MP2T", action, ""]
