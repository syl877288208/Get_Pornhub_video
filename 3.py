#!python

import requests
import re
import datetime
import os
import sys
from contextlib import closing


class ProgressBar(object):
    def __init__(self, title,
                 count=0.0,
                 run_status=None,
                 fin_status=None,
                 total=100.0,
                 unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "【%s】%s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.statue)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (self.title, self.status,
                             self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\n\r"
        if self.count >= self.total:
            end_str = '\n\r'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)


def save_file(the_url, path):
    print("--------------------------------------------------------")
    time1 = datetime.datetime.now()
    print(str(time1)[: -7])
    if os.path.isfile(path):
        file_size = str(os.path.getsize(path)/1024/1024)
        print("File " + path + "(" + file_size + "MB) already exists")
        return
    else:
        print("Downloading " + path + "...")

    file = requests.get(the_url, stream=True)
    file.raise_for_status()
    with closing(file) as response:
        chunk_size = 1024
        content_size = int(response.headers['content-length']) / 1024
        progress = ProgressBar("AV", total=content_size,
                               unit="MB",
                               chunk_size=chunk_size,
                               run_status="正在下载",
                               fin_status="下载完成")
        with open(path, "wb") as code:
            for data in file.iter_content(5120000):
                code.write(data)
                progress.refresh(count=(len(data)/1024))
    time2 = datetime.datetime.now()
    print(str(time2)[:-7])
    print(path + " Done")
    use_time = time2 - time1
    print("Time used: "+str(use_time)[:-7])
    file_size = os.path.getsize(path)/1024/1024
    print("File size: "+str(file_size)+" MB, Speed: "+str(file_size/(use_time.total_seconds()))[:4]+"MB/s")



def download_file(urls):
    res = requests.get(urls)
    res.raise_for_status()
    res_text = res.text
    while len(res_text) < 100:
        print("Try again...")
        res = requests.get(urls)
        res.raise_for_status()
        res_text = res.text
    print("All length: " + str(len(res_text)))

    title_begin = res_text.find("<title>")
    title_end = res_text.find("</title>")
    title = res_text[title_begin + 7:title_end - 14]
    title = title.replace(' ', '_')
    title = list(filter(lambda x: x in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ _-", title))
    title_name = "".join(title)
    path = title_name + ".mp4"

    quality = ["720", "480", "240"]
    for i in quality:
        find_position = res_text.find("\"quality\":\"" + i + "\"")
        if find_position > 0:
            print("Quality: " + i + "P")
            break
    to_find = res_text[find_position:find_position + 4000]
    pattern = re.compile(r"\"videoUrl\":\"[^\"]*\"")
    match = pattern.search(to_find)
    if match:
        the_url = match.group()
    the_url = the_url[12:-1]  # the real url
    the_url = the_url.replace("\\/", "/")

    save_file(the_url, path)

txt = sys.argv[1]
file = open(txt)
file_content = file.readlines()
for i in range(0, len(file_content)):
    s = file_content[i]
    s = s.replace("\n","")
    file_content[i] = s

video_urls = file_content
print(str(len(video_urls)) + " videos!")

for url in video_urls:
    download_file(url)
print("All done!!!")
