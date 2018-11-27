import requests
import csv
from retrying import retry
from json import JSONDecodeError
import json


class lagouspider():
    def __init__(self):
        self.header = {'Host': 'www.lagou.com',
                          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
                          'Accept': 'application/json, text/javascript, */*; q=0.01',
                          'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
                          'Accept-Encoding': 'gzip, deflate, br',
                          'Referer': 'https://www.lagou.com/jobs/list_Python?labelWords=&fromSearch=true&suginput=',
                          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                          'X-Requested-With': 'XMLHttpRequest',
                          'X-Anit-Forge-Token': 'None',
                          'X-Anit-Forge-Code': '0',
                          'Content-Length': '26',
                          'Cookie': '_ga=GA1.2.1015646365.1538989463; user_trace_token=20181008170425-277ca381-cad9-11e8-bb68-5254005c3644; LGUID=20181008170425-277caaa8-cad9-11e8-bb68-5254005c3644; index_location_city=%E5%85%A8%E5%9B%BD; JSESSIONID=ABAAABAAAGGABCB4878F933065B5D43F6FB0748D8A0E39E; LGSID=20181018091439-2f6bfe7d-d273-11e8-bda4-5254005c3644; PRE_UTM=; PRE_HOST=www.google.com; PRE_SITE=https%3A%2F%2Fwww.google.com%2F; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; _gid=GA1.2.465338117.1539825277; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1538989463,1539825277,1539825286,1539825338; TG-TRACK-CODE=index_search; _gat=1; LGRID=20181018094311-2bef568a-d277-11e8-8058-525400f775ce; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1539826990; SEARCH_ID=44a9a700439e406a80372da370820d72',
                          'Connection': 'keep-alive',
                          'Pragma': 'no-cache',
                          'Cache-Control': 'no-cache'}
        self.start_url="https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false"

    def get_post(self,url,data):
        response=requests.post(url,headers=self.header,data=data)
        return response.text
    def get_data(self,kd,pn):
        data={
            "first": "false",
            "pn": pn,
            "kd": kd
        }
        return data
    def json2dict(self,infos):
        try:
            items=json.loads(infos)
            return items
        except JSONDecodeError as e:
            print(e)

    @retry(stop_max_attempt_number=3)
    def get_info(self,items,item):
        try:
            for info in items["content"]["positionResult"]["result"]:
                item['职位'] = info['positionName']
                item['职位发布时间'] = info['createTime']
                # 把字典里面的东西提取出来，再加上一个名字
                item['工作经验'] = info['workYear']
                item['学历要求'] = info['education']
                item['工资'] = info['salary']
                item['职位诱惑'] = info['companyLabelList'] if len(info['companyLabelList']) > 0 else '空字段'
                item['职位标签'] = info['positionLables'] if len(info['positionLables']) > 0 else '空字段'
                item['公司名称'] = info['companyFullName']
                yield item

                #yield item
        except :
            pass


    def run(self,key):
        num=1
        item = {}
        while 1:
            try:
                data = self.get_data(kd=key, pn=num)
                infos = self.get_post(self.start_url, data=data)
                items=self.json2dict(infos)
                page=items["content"]["pageNo"]
                print("*" * 100)
                print("正在爬取第%d页"%page)
                print("*"*100)
                try:
                    for i in self.get_info(items,item):
                        with open(key+'拉钩网职位信息.csv', 'a', newline='') as f:
                            writer = csv.DictWriter(f, headers)
                            writer.writerow(i)
                except PermissionError as e :
                    print(e)
                except UnicodeEncodeError as f:
                    print(f)
                num+=1
                if page==0:
                    print("爬取结束")
                    break
            except TypeError as m:
                print(m)

if __name__ == '__main__':
    headers = ['职位', '职位发布时间', '工作经验', '学历要求', '工资', '职位诱惑', '职位标签', '公司名称']
    key=input("请输入需要要爬取职位的关键字:")
    with open(key+'拉钩网职位信息.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
    spider=lagouspider()
    spider.run(key)
















