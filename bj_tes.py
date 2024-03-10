import time
import os
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import re

urls = [
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IkJlaWppbmciICYmIG9yZz0iQ2hpbmEgVW5pY29tIEJlaWppbmcgUHJvdmluY2UgTmV0d29yayI%3D",  # beijing
    "https://www.zoomeye.org/searchResult?q=udpxy%20+subdivisions:%22%E5%8C%97%E4%BA%AC%22%20+organization:%22%E4%B8%AD%E5%9B%BD%E8%81%94%E9%80%9A%22"  # beijing
    ]

def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/status"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)

    return modified_urls


def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None

def build_channel_urls(valid_urls, channels):
    channel_urls = []
    for valid_url in valid_urls:
        for channel in channels:
            ip = valid_url.split("//")[1].split(":")[0]
            port = valid_url.split(":")[-1]
            channel_ip_port = channel.replace('ip', ip).replace('port', port)
            channel_urls.append(channel_ip_port)
    return channel_urls

def remove_status_from_urls(urls):
    modified_urls = []
    for url in urls:
        # 删除每个url中的'/status'
        clean_url = url.replace('/status', '')
        modified_urls.append(clean_url)
    return modified_urls

results = []

channels = [
    "CCTV-1 HD,http://ip:port/rtp/239.3.1.129:8008",
    "CCTV-2 HD,http://ip:port/rtp/239.3.1.60:8084",
    "CCTV-3 HD,http://ip:port/rtp/239.3.1.172:8001",
    "CCTV-4 HD,http://ip:port/rtp/239.3.1.105:8092",
    "CCTV-5 HD,http://ip:port/rtp/239.3.1.173:8001",
    "CCTV-5+ HD,http://ip:port/rtp/239.3.1.130:8004",
    "CCTV-6 HD,http://ip:port/rtp/239.3.1.174:8001",
    "CCTV-7 HD,http://ip:port/rtp/239.3.1.61:8104",
    "CCTV-8 HD,http://ip:port/rtp/239.3.1.175:8001",
    "CCTV-9 HD,http://ip:port/rtp/239.3.1.62:8112",
    "CCTV-10 HD,http://ip:port/rtp/239.3.1.63:8116",
    "CCTV-11 HD,http://ip:port/rtp/239.3.1.152:8120",
    "CCTV-12 HD,http://ip:port/rtp/239.3.1.64:8124",
    "CCTV-13 HD,http://ip:port/rtp/239.3.1.124:8128",
    "CCTV-14 HD,http://ip:port/rtp/239.3.1.65:8132",
    "CCTV-15 HD,http://ip:port/rtp/239.3.1.153:8136",
    "CCTV-16 奥林匹克[HDR],http://ip:port/rtp/239.3.1.183:8001",
    "CCTV-16 奥林匹克HD,http://ip:port/rtp/239.3.1.184:8001",
    "CCTV-17 HD,http://ip:port/rtp/239.3.1.151:8144",
    "BRTV北京卫视HD,http://ip:port/rtp/239.3.1.241:8000",
    "BRTV新闻HD,http://ip:port/rtp/239.3.1.159:8000",
    "BRTV影视HD,http://ip:port/rtp/239.3.1.158:8000",
    "BRTV文艺HD,http://ip:port/rtp/239.3.1.242:8000",
    "BRTV财经HD,http://ip:port/rtp/239.3.1.116:8000",
    "BRTV生活HD,http://ip:port/rtp/239.3.1.117:8000",
    "BRTV青年HD,http://ip:port/rtp/239.3.1.118:8000",
    "BRTV纪实科教HD,http://ip:port/rtp/239.3.1.115:8000",
    "BRTV卡酷少儿HD,http://ip:port/rtp/239.3.1.189:8000",
    "BRTV冬奥纪实HD,http://ip:port/rtp/239.3.1.243:8000",
    "BRTV冬奥纪实[HDR],http://ip:port/rtp/239.3.1.120:8000",
    "BRTV冬奥纪实[超清],http://ip:port/rtp/239.3.1.121:8000",
    "BRTV体育休闲[超清],http://ip:port/rtp/239.3.1.243:8000",
    "BTV国际频道,http://ip:port/rtp/239.3.1.235:8000",
    "爱上4K[超清],http://ip:port/rtp/239.3.1.236:2000",
    "4K超清[超清],http://ip:port/rtp/239.3.1.249:8001",
    "淘电影HD,http://ip:port/rtp/239.3.1.250:8001",
    "每日影院HD,http://ip:port/rtp/239.3.1.111:8001",
    "星影,http://ip:port/rtp/239.3.1.94:4120",
    "动作影院,http://ip:port/rtp/239.3.1.92:4120",
    "光影,http://ip:port/rtp/239.3.1.84:4120",
    "喜剧影院,http://ip:port/rtp/239.3.1.91:4120",
    "家庭影院,http://ip:port/rtp/239.3.1.93:4120",
    "精选,http://ip:port/rtp/239.3.1.74:4120",
    "经典电影,http://ip:port/rtp/239.3.1.195:9024",
    "纪实人文HD,http://ip:port/rtp/239.3.1.212:8060",
    "金鹰纪实HD,http://ip:port/rtp/239.3.1.58:8156",
    "风尚生活HD,http://ip:port/rtp/239.3.1.114:8001",
    "地理,http://ip:port/rtp/239.3.1.71:4120",
    "淘剧场HD,http://ip:port/rtp/239.3.1.95:8001",
    "幸福剧场HD,http://ip:port/rtp/239.3.1.112:8001",
    "淘娱乐HD,http://ip:port/rtp/239.3.1.100:8001",
    "幸福娱乐HD,http://ip:port/rtp/239.3.1.113:8001",
    "淘BabyHD,http://ip:port/rtp/239.3.1.238:8001",
    "萌宠TVHD,http://ip:port/rtp/239.3.1.102:8001",
    "湖南卫视HD,http://ip:port/rtp/239.3.1.132:8012",
    "东方卫视HD,http://ip:port/rtp/239.3.1.136:8032",
    "浙江卫视HD,http://ip:port/rtp/239.3.1.137:8036",
    "江苏卫视HD,http://ip:port/rtp/239.3.1.135:8028",
    "深圳卫视HD,http://ip:port/rtp/239.3.1.134:8020",
    "广东卫视HD,http://ip:port/rtp/239.3.1.142:8048",
    "安徽卫视HD,http://ip:port/rtp/239.3.1.211:8064",
    "天津卫视HD,http://ip:port/rtp/239.3.1.141:1234",
    "重庆卫视HD,http://ip:port/rtp/239.3.1.122:8160",
    "山东卫视HD,http://ip:port/rtp/239.3.1.209:8052",
    "黑龙江卫视HD,http://ip:port/rtp/239.3.1.133:8016",
    "河北卫视HD,http://ip:port/rtp/239.3.1.148:8072",
    "辽宁卫视HD,http://ip:port/rtp/239.3.1.210:8056",
    "湖北卫视HD,http://ip:port/rtp/239.3.1.138:8044",
    "吉林卫视HD,http://ip:port/rtp/239.3.1.240:8172",
    "贵州卫视HD,http://ip:port/rtp/239.3.1.149:8076",
    "东南卫视HD,http://ip:port/rtp/239.3.1.156:8148",
    "江西卫视HD,http://ip:port/rtp/239.3.1.123:8164",
    "海南卫视,http://ip:port/rtp/239.3.1.45:8304",
    "云南卫视,http://ip:port/rtp/239.3.1.26:8108",
    "兵团卫视,http://ip:port/rtp/239.3.1.144:4120",
    "厦门卫视,http://ip:port/rtp/239.3.1.143:4120",
    "四川卫视,http://ip:port/rtp/239.3.1.29:8288",
    "南方卫视,http://ip:port/rtp/239.3.1.161:8001",
    "宁夏卫视,http://ip:port/rtp/239.3.1.46:8124",
    "山西卫视,http://ip:port/rtp/239.3.1.42:8172",
    "广西卫视,http://ip:port/rtp/239.3.1.39:8300",
    "新疆卫视,http://ip:port/rtp/239.3.1.48:8160",
    "河南卫视,http://ip:port/rtp/239.3.1.27:8128",
    "甘肃卫视,http://ip:port/rtp/239.3.1.49:8188",
    "西藏卫视,http://ip:port/rtp/239.3.1.47:8164",
    "三沙卫视,http://ip:port/rtp/239.3.1.155:4120",
    "陕西卫视,http://ip:port/rtp/239.3.1.41:8140",
    "青海卫视,http://ip:port/rtp/239.3.1.44:8184",
    "内蒙古卫视,http://ip:port/rtp/239.3.1.43:8176",
    "中国交通HD,http://ip:port/rtp/239.3.1.188:8001",
    "朝阳融媒HD,http://ip:port/rtp/239.3.1.163:8001",
    "通州融媒HD,http://ip:port/rtp/239.3.1.221:8001",
    "密云电视台HD,http://ip:port/rtp/239.3.1.154:8001",
    "延庆电视台,http://ip:port/rtp/239.3.1.187:8001",
    "房山电视台,http://ip:port/rtp/239.3.1.96:8001",
    "CCTV-4 中文国际 欧洲HD,http://ip:port/rtp/239.3.1.213:4220",
    "CCTV-4 中文国际 美洲HD,http://ip:port/rtp/239.3.1.214:4220",
    "CGTN 新闻HD,http://ip:port/rtp/239.3.1.215:4220",
    "CGTN 记录HD,http://ip:port/rtp/239.3.1.216:4220",
    "CGTN 西班牙语HD,http://ip:port/rtp/239.3.1.217:4220",
    "CGTN 法语HD,http://ip:port/rtp/239.3.1.218:4220",
    "CGTN 阿拉伯语HD,http://ip:port/rtp/239.3.1.219:4220",
    "CGTN 俄语HD,http://ip:port/rtp/239.3.1.220:4220",
    "睛彩竞技HD,http://ip:port/rtp/239.3.1.125:8001",
    "睛彩篮球HD,http://ip:port/rtp/239.3.1.126:8001",
    "睛彩羽毛球HD,http://ip:port/rtp/239.3.1.127:8001",
    "睛彩广场舞HD,http://ip:port/rtp/239.3.1.128:8001",
    "茶频道HD,http://ip:port/rtp/239.3.1.165:8001",
    "体育赛事HD,http://ip:port/rtp/239.3.1.157:8176",
    "淘精彩HD,http://ip:port/rtp/239.3.1.178:8001",
    "快乐垂钓HD,http://ip:port/rtp/239.3.1.164:8001",
    "大健康HD,http://ip:port/rtp/239.3.1.251:8001",
    "CETV1HD,http://ip:port/rtp/239.3.1.57:8152",
    "CETV2,http://ip:port/rtp/239.3.1.54:4120",
    "CETV3,http://ip:port/rtp/239.3.1.55:4120",
    "CETV4,http://ip:port/rtp/239.3.1.56:4120",
    "少儿动画,http://ip:port/rtp/239.3.1.199:9000",
    "热播剧场,http://ip:port/rtp/239.3.1.194:9020",
    "解密,http://ip:port/rtp/239.3.1.75:4120",
    "军事,http://ip:port/rtp/239.3.1.76:4120",
    "军旅剧场,http://ip:port/rtp/239.3.1.68:4120",
    "动画,http://ip:port/rtp/239.3.1.80:4120",
    "古装剧场,http://ip:port/rtp/239.3.1.69:4120",
    "台球,http://ip:port/rtp/239.3.1.85:4120",
    "嘉佳卡通,http://ip:port/rtp/239.3.1.147:9268",
    "国学,http://ip:port/rtp/239.3.1.77:4120",
    "城市剧场,http://ip:port/rtp/239.3.1.67:4120",
    "墨宝,http://ip:port/rtp/239.3.1.83:4120",
    "好学生,http://ip:port/rtp/239.3.1.81:4120",
    "山东教育,http://ip:port/rtp/239.3.1.52:4120",
    "戏曲,http://ip:port/rtp/239.3.1.78:4120",
    "收视指南,http://ip:port/rtp/239.3.1.193:8012",
    "早教,http://ip:port/rtp/239.3.1.79:4120",
    "武侠剧场,http://ip:port/rtp/239.3.1.90:4120",
    "武术,http://ip:port/rtp/239.3.1.87:4120",
    "爱生活,http://ip:port/rtp/239.3.1.86:4120",
    "美人,http://ip:port/rtp/239.3.1.73:4120",
    "美妆,http://ip:port/rtp/239.3.1.72:4120",
    "财富天下,http://ip:port/rtp/239.3.1.53:9136",
    "足球,http://ip:port/rtp/239.3.1.89:4120",
    "金鹰卡通,http://ip:port/rtp/239.3.1.51:9252",
    "鉴赏,http://ip:port/rtp/239.3.1.82:4120",
    "音乐现场,http://ip:port/rtp/239.3.1.70:4120",
    "高网,http://ip:port/rtp/239.3.1.88:4120",
    "魅力时尚,http://ip:port/rtp/239.3.1.196:9012"
    # ... 加入其他频道的信息
]

for url in urls:
    try:
        # 创建一个Chrome WebDriver实例
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    
        driver = webdriver.Chrome(options=chrome_options)
        # 使用WebDriver访问网页
        driver.get(url)  # 将网址替换为你要访问的网页地址
        time.sleep(10)
        # 获取网页内容
        page_content = driver.page_source
    
        # 关闭WebDriver
        driver.quit()
    
        # 查找所有符合指定格式的网址
        pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式，如http://8.8.8.8:8888
        urls_all = re.findall(pattern, page_content)
        # urls = list(set(urls_all))  # 去重得到唯一的URL列表
        urls = set(urls_all)  # 去重得到唯一的URL列表
        x_urls = []
        for url in urls:  # 对urls进行处理，ip第四位修改为1，并去重
            url = url.strip()
            ip_start_index = url.find("//") + 2
            ip_end_index = url.find(":", ip_start_index)
            ip_dot_start = url.find(".") + 1
            ip_dot_second = url.find(".", ip_dot_start) + 1
            ip_dot_three = url.find(".", ip_dot_second) + 1
            base_url = url[:ip_start_index]  # http:// or https://
            ip_address = url[ip_start_index:ip_dot_three]
            port = url[ip_end_index:]
            ip_end = "1"
            modified_ip = f"{ip_address}{ip_end}"
            x_url = f"{base_url}{modified_ip}{port}"
            x_urls.append(x_url)
        urls = set(x_urls)  # 去重得到唯一的URL列表
    
        valid_urls = []
        
        #   多线程获取可用url
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            for url in urls:
                url = url.strip()
                modified_urls = modify_urls(url)
                for modified_url in modified_urls:
                    futures.append(executor.submit(is_url_accessible, modified_url))
    
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid_urls.append(result)
        for url in valid_urls:
            print(url)

        # 在这里您已经收集了所有有效的URLs（valid_urls）
        valid_urls = remove_status_from_urls(valid_urls) # 删除每个URL中的'/status'

        # 构建频道URLs并保存到文件
        if valid_urls:
            # 调用上面定义的函数来构建每个频道的播放地址
            channel_urls = build_channel_urls(valid_urls, channels)
            #print(channel_urls)
    except:
        continue

results = set(channel_urls)   # 去重得到唯一的URL列表
results = sorted(results)
#print(results)

# 连接所有结果，每个结果后面加上换行符
final_text = "\n".join(results)

# 在整个文本前加上前缀“临时抓取,#genre#”
final_text = "北京联通,#genre#\n" + final_text

# 写入文件，确保只在最开始的时候加上了前缀
with open("bj_un.txt", 'w', encoding='utf-8') as file:
    #for result in results:
        file.write(final_text)
        #file.write(result)
        print('final')

