# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os
import time
import re
from multiprocessing import Queue, Process
from threading import Thread
from urllib.parse import unquote

# 待解决问题
# 文件下载不完整的问题(目前通过比较文件大小判断是否下载完整，可以支持断点续传吗？)
# 写日志记录源文件大小和下载后的文件大小
# closing的作用？

class Code_spider(object):
    def __init__(self):
        self.mainurl = 'http://xiumeitu.herokuapp.com'
        # 有些网站会有防盗链，原理是检查 HTTP的referer头，如果没有referer，会抓取不了数据
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36','referer':"http://www.mm131.com/xinggan/530.html"}
        self.main_folder= 'img/'
        self.images_url=[]
        self.title=[]
        # 创建消息队列，存放下载链接
        self.q = Queue()



# 创建soup对象
    def creat_soup(self,url):
        '''
        该函数返回一个url的soup对象
        :param url:一个页面的链接
        '''
        # 获取网页，得到一个response对象
        response = requests.get(url)
        # 指定自定义编码，让文本按指定的编码进行解码，因为网站的charset = utf-8
        response.encoding = 'utf-8'
        # 使用解码后的数据创建一个soup对象，指定HTML解析器为Python默认的html.parser
        return BeautifulSoup(response.text,'html.parser')


    #获取各层地址和标题
    def get_link(self):

        #第一层地址
        self.pages_url = [self.mainurl]
        # 将当前图片类型的每一页的链接存储起来，每一页的链接后跟list_position_页码.html，这里只存储5页
        for page in range(2, 50):
            self.pages_url.append(self.mainurl + '/' + str(page))
        print("第一层地址获取完毕！")
        self.alphas_url = []
        #图集标题
        self.title = []
        self.images_url = []
        #第二层地址
        for page_url in self.pages_url:
            # 调用函数，创建页面链接的soup对象
            soup = self.creat_soup(page_url)
            # 查找当前页面所有的图集信息，find_all 返回的是一个列表，先找到所含有需要链接的那段信息，F12
            atlas_information = soup.find_all("div",class_="record-container")
            for information in atlas_information:
                self.alphas_url.append(self.mainurl+information.find('a').get('href'))
                #存储图集标题
                self.title.append(information.find('h2').string)
        print("第二层地址获取完毕！大小：{}.{}".format(len(self.alphas_url),len(self.title)))
         #alphas_url为图集总列表：http://xiumeitu.herokuapp.com/record/5ad34f4b91dba56e47085cfe

        for alpha1_url in self.alphas_url :
            #筛选有效网址，本网址有些网页只有标题，没有图片。。。404就是网页不存在
            code = requests.get(alpha1_url+"/3").status_code
            print(code)
            length = len(self.alphas_url)
            if code == 404 :
                index= self.alphas_url.index(alpha1_url)
                print("图集{}无效，删除..{}". format(self.title[index],alpha1_url))
                #删除列表的值
                self.alphas_url.pop(index)
                self.title.pop(index)
        
        print("有效地址筛选完毕！地址集合数量：{}/标题数量{}".format(len(self.alphas_url),len(self.title)))

        for alpha_url in self.alphas_url:
            betas_url=[alpha_url]
            sigmas_url=[]

            #生成图集所有页面地址
            for i in range(2, 15):
                betas_url.append(alpha_url + "/" + str(i))
            for beta_url in betas_url:
                print("获取链接中"+ beta_url)
                soup = self.creat_soup(beta_url)
                #F12检查图片的信息，找到对应的class
                detail_info=soup.find_all("div",class_="record-container")
                for tmp_info in detail_info:
                    #找到图片真正地址
                    sigmas_url.append(tmp_info.find('img').get('src'))
            self.images_url.append(sigmas_url)
        if len(self.images_url)==len(self.title):
            self.address_comp = 1
            print("图集地址校验完毕")
        else:
            self.address_comp = 0
            print("图集校验错误")
    #将获取的标题和网址写入文件
    def writefile(self,title_list,url_lists,file):
        print("start to writ file!")
        if len(title_list)==len(url_lists):
            a=len(title_list)
            # 设置文件对象
            with open(file,"w") as f:
                 for i in range(a):
                     #写标题数据
                     f.write("title="+title_list[i]+'\n')
                     #写图片网址
                     for j in url_lists[i]:
                        k = str(j)+'\n'  #将其中每一个列表规范化成字符串
                        f.write(k)
            print("file writed done!")
        else:
            print("list error!")
    #从文件中获取标题和网页
    def readfile(self,text):
        print("start read file!")
        image_url=[]
        last_t=0
        now_t=0
        for line in open(text,"r"):
            #去掉换行符'\n"
            line=line[:-1]
            #判断是否为标题
            if re.match("title=",line):
                now_t=1
            else:
                now_t=0
            #上一行不是标题，本行是标题，则写入标题集合
            if last_t==0 and now_t==1:
                self.title.append(re.sub("title=","",line))
            # 上一行是标题，本行也是标题，则覆盖上一行标题
            elif last_t == 1 and now_t == 1:
                self.title.pop()
                self.title.append(re.sub("title=","",line))
            # 上一行是标题，本行不是标题，将子集合添加到总集合，并重新建网址子集合
            elif last_t == 1 and now_t == 0:
                if image_url != []:
                    self.images_url.append(image_url)
                image_url=[line]
            # 上一行不是标题，本行不是标题，添加到网址子集合
            else:
                image_url.append(line)
            last_t=now_t
        #将最后一个子集合添加
        self.images_url.append(image_url)
        print("file read finished!")

    #从队列中获取下载地址并下载
    def download(self,n):
        #显示队列大小
        print(self.q.qsize())
        down_nr=0
        down_title=""
        #获取队列内容
        down_list=self.q.get()
        folder=""
        for i in self.images_url:
            if down_list==i:
                down_title=self.title[self.images_url.index(i)]
                folder = self.main_folder + down_title + '/'
                try:
                    # 判断文件夹是否存在
                    if os.path.exists(folder) == False:
                        # 创建文件夹
                        os.makedirs(folder)
                except:
                    pass
                break
        for download_url in down_list:
            #第几张图片
            down_nr= down_list.index(download_url)
            # get函数发送图片链接访问请求
            html = requests.get(download_url,headers = self.headers)
            # 保存图片至指定的文件夹，并将文件进行命名
            image_name = folder + str(down_nr + 1) + '.jpg'
            # 以byte形式将图片数据写入
            with open(image_name,'wb') as file:
                file.write(html.content)
            print('正在下载图集{}第{}张图片...by线程{}'.format(down_title,down_nr + 1,n))

    def work(self):
        # 程序运行开始提示
        print("程序于 {} 开始启动，请等待...".format(time.ctime()))
        # 获取页面的所有图集链接
        self.get_link()
        #将获取的网址写入文件
        self.writefile(self.title,self.images_url,"url.txt")
        #读取文件内容
        self.readfile("url.txt")
        #images_url为2层列表
        for image_url in self.images_url:
            #将第二层列表放进队列
            self.q.put(image_url)
        # 开启多线程
        #当队列不为空的时候循环下载
        while self.q.empty() == 0:
            try:
                #初始化线程集合
                L = []
                #多线程调用
                for i in range(20):
                    th = Thread(target=self.download, args=(i + 1,))
                    # th = Process(target=spider.down_load, args=(i+1,))
                    th.start()
                    L.append(th)

                for th in L:
                    th.join()
            except:
                break
        print("download..finished!")
#主程序
if __name__ == '__main__':
    start_time = time.time()

    spider = Code_spider()
    spider.work()

    end_time = time.time()

    print("爬取总时间:",end_time-start_time)

