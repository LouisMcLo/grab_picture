import requests
import json
import urllib.request
import time
'''
原文网址：https://www.cnblogs.com/dearvee/p/6558571.html
需要的图片资料不在主url  即 http://pic.sogou.com/pics/recommend?category=%B1%DA%D6%BD&from=home#%E5%85%A8%E9%83%A8%2610里面。
因此考虑可能该元素是动态的，细心的同学可能会发现，当在网页内，向下滑动鼠标滚轮，图片是动态刷新出来的，也就是说，
该网页并不是一次加载出全部资源，而是动态加载资源。这也避免了因为网页过于臃肿，而影响加载速度。
我们是要找到所有图片的真正的url，最后找的位置F12>>Network>>XHR>>(点击XHR下的文件)>>Preview
'''
def getSogouImag(length,path):
    n = length
    imgs = requests.get('http://pic.sogou.com/pics/channel/getAllRecomPicByTag.jsp?category=%E5%A3%81%E7%BA%B8&tag=%E5%85%A8%E9%83%A8&start=0&len='+str(n)+'&width=1440&height=900')
    jd = json.loads(imgs.text)
    jd = jd['all_items']
    imgs_url = []
    for j in jd:
        imgs_url.append(j['pic_url'])
    m = 0
    for img_url in imgs_url:
            print('***** '+str(m)+'.jpg *****'+'   Downloading...')
            urllib.request.urlretrieve(img_url,path+str(m)+'.jpg')
            m = m + 1
            time.sleep(1)
    print('Download complete!')

getSogouImag(2000,'C:/Users/louis/PycharmProjects/proj123/venv/Include/壁纸/')
