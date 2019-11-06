# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os
import time
import re

# 程序运行开始提示
print("程序于 {} 开始启动，请等待...".format(time.ctime()))
# 美女图片类型和对应的页面序列位置，图片类型为键，位置为 值
# 这个位置用于图集的链接，如list_6_3.html，6即为性感美女的序列位置 http://www.win4000.com/meinvtag4_1.html
girls_images_type = {'xinggan':'4','cosplay':'26','youxi':'7','kongjie':'6'}

# 创建soup对象
def creat_soup(url):
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

def pages_url(position):
    #指定主页
    url = 'http://www.win4000.com/'
    # 初始化网页
    pages_url = []
    # 将当前图片类型的每一页的链接存储起来，每一页的链接后跟list_position_页码.html，这里只存储5页
    for page in range(1,6):
        pages_url.append(url + 'meinvtag' + position + '_'+ str(page) + '.html')
    # 函数返回某一个图片类型的全部页面链接
    return pages_url



def atlas(pages_url):
    '''
    该函数用于存储某一个页面的所有图集链接
    :param pages_url:页面链接，可以是列表
    '''
    # 用于存储每一个图集链接的列表
    atlas_url = []
    #图集标题
    title = []
    for page_url in pages_url:
        # 调用函数，创建页面链接的soup对象
        soup = creat_soup(page_url)
        # 查找当前页面所有的图集信息，find_all 返回的是一个列表，先找到所含有需要链接的那段信息，F12
        atlas_information = soup.find_all("ul",class_="clearfix")
        for information in atlas_information:
            #进一步缩小查找范围,直接find('a').get('href')会丢失部分信息
            atlas_information2 = information.find_all("li")
            for information2 in atlas_information2:
                # 筛选符合要求的网址信息
                if re.search('http://www.win4000.com/meinv',information2.find('a').get('href')) :
                    # 将符合条件的链接，即 每一个图集的链接加入到列表中
                    atlas_url.append(information2.find('a').get('href'))
                    #存储图集名称
                    title.append(information2.find('p').string)
    # 函数返回某一个页面的全部图集链接和图集名称
    return atlas_url,title


def save_images(atlas_url,title):
    '''
    该函数用于将某一图集的所有图片保存下来
    :param atlas_url:图集链接，可以是个列表
    '''
    # 共有多少个图集
    length = len(atlas_url)
    # 已下载图集
    count = 1
    for url in atlas_url :
        #照片元组清空
        images_url = []
        # 指定文件夹名为在title元组的元素,对应url在atlas_url中的位置
        file_folder = title[atlas_url.index(url)]
        # 将图片文件夹保存在程序文件所在目录的imgase目录下
        folder = 'images/' + file_folder + '/'
        if os.path.exists(folder) == False:# 判断文件夹是否存在
            os.makedirs(folder) # 创建文件夹
        for i in range(1,99):
            # 当前网站格式是atlas_url中间穿插编号：http://www.win4000.com/meinv189530_x.html,需要把得到的网址处理一下
            tmp_url = re.sub(".html","",url)
            # 在.html前加上_x,生成新链接
            tmp_new_url = (tmp_url + '_' + str(i) + '.html')
            # 调用函数，创建图集链接的soup对象
            soup = creat_soup(tmp_new_url)
            #F12检查图片的信息，找到对应的class
            detail_info=soup.find_all("div",class_="pic-meinv")
            for tmp_info in detail_info:
                #找到图片真正地址
                images_url.append(tmp_info.find('img').get('url'))
        # 有些网站会有防盗链，原理是检查 HTTP的referer头，如果没有referer，会抓取不了数据
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36','referer':"http://www.mm131.com/xinggan/530.html"}
        # 开始下载提示，等待2秒后开始下载
        print("开始下载图集 {}，剩余图集 {}".format(file_folder,length - count))
        time.sleep(2)

        for index,image_url in enumerate(images_url):
            # get函数发送图片链接访问请求
            html = requests.get(image_url,headers = headers)
            # 保存图片至指定的文件夹，并将文件进行命名
            image_name = folder + str(index + 1) + '.jpg'
            # 以byte形式将图片数据写入
            with open(image_name,'wb') as file:
                file.write(html.content)
            print('第{}张图片下载完成,开始下载第{}张图片...'.format(index+1,index+2))
        # 已下载图集加1
        count += 1
    print("当前图集图片已下载完成\n")


# 获取某一图片类型的所有页面链接，可以使用循环遍历字典 girls_images_type，获取所有的图片类型的所有页面链接，
# 那样运行时间太长，这里为了演示，只取其中一个图片类型
pages_url = pages_url('4')
# 获取页面的所有图集链接
atlas_url,title = atlas(pages_url)
# 下载图集的图片
save_images(atlas_url,title)