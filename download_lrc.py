import requests
from bs4 import BeautifulSoup
import re
import json
import os


#请求的消息头，为固定的模式
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Referer': 'https://music.163.com/',
    'Host': 'music.163.com'
}

#通过一个歌手id下载这个歌手的所有歌词
def get_music_ids_by_musican_id(singer_id):
    os.chdir('/Users/yinchenhao/Documents/lrc')
    singer_url = 'http://music.163.com/artist?'+ 'id='+str(singer_id)
    r = requests.get(singer_url, headers=headers).text
    soupObj = BeautifulSoup(r,'lxml')
    song_ids = soupObj.find('textarea').text
    singer_name = soupObj.find('title').text
    jobj = json.loads(song_ids)
    name = re.match('(.*?) - 歌手', singer_name).group(1)
    for item in jobj:
        text = download_by_music_id(item['id'])
        if text != '歌词不存在!':
            song_name = name + '-' + item['name'] + '.txt'
            result_name = re.sub('\(.*?\)', '', song_name)
            file = open(result_name,'a',encoding='utf-8')
            file.write(text)
            file.close()
            file = open('all_lrc.txt','a',encoding='utf-8')
            file.write(text)
            file.close()

#根据音乐id获取歌词内容
def download_by_music_id(music_id):
    url = 'http://music.163.com/api/song/lyric?'+ 'id=' + str(music_id)+ '&lv=1&kv=1&tv=-1'
    r = requests.get(url)
    json_obj = r.text
    j = json.loads(json_obj)
    if 'lrc' in j:
        lrc = j['lrc']['lyric']
        pat = re.compile(r'\[.*\]')  #这里几行代码是把歌词中的空格和符号之类的去掉
        lrc = re.sub(pat,"",lrc)
        lrc = lrc.strip()
        return lrc
    else:
        return '歌词不存在!'

#对歌词文本做粗处理，并且删除作词作曲等信息
def format_content(content):
    content = content.replace(u'\xa0', u' ')
    content = re.sub(r'\[.*?\]','',content)
    content = re.sub(r'\s*作曲.*\n','',content)
    content = re.sub(r'\s*作词.*\n','',content)
    content = re.sub(r'.*:','',content)
    content = re.sub(r'.*：','',content)
    content = content.replace('\n', ' ')
    return content

# 读取要下载的歌词的列表
# 在这里我将网易云上的所有需要爬的歌手id保存成文件
def download_sings_by_singerId():
    os.chdir('/Users/yinchenhao/Documents/lrc/')
    singer_id_arr = []
    file = open('singer_list.txt')
    for lines in file.readlines():
        singerArr = lines.split(' ')
        singerId = singerArr[1]
        singer_id_arr.append(singerId)
    write_songs_by_singers(singer_id_arr)


#对歌词进行写操作
def write_songs_by_singers(singer_id_arr):
    os.chdir('/Users/yinchenhao/Documents/lrc/temp')
    for singer_id in singer_id_arr:
        singer_url = 'http://music.163.com/artist?' + 'id=' + str(singer_id)
        r = requests.get(singer_url, headers=headers).text
        soupObj = BeautifulSoup(r, 'lxml')
        song_ids = soupObj.find('textarea').text
        singer_name = soupObj.find('title').text
        jobj = json.loads(song_ids)
        name = re.match('(.*?) - 歌手', singer_name).group(1)
        for item in jobj:
            text = download_by_music_id(item['id'])
            if text != '歌词不存在!':
                song_name = name + '-' + item['name'] + '.txt'
                result_name = re.sub('\(.*?\)', '', song_name)
                file = open(result_name, 'a', encoding='utf-8')
                file.write(text)
                file.close()
                file = open('all_lrc.txt', 'a', encoding='utf-8')
                file.write(text)
                file.close()
                singer_content = open(name + '.txt', 'a', encoding='utf-8')
                singer_content.write(text)
                singer_content.close()


# 处理所有的歌词，将每个歌手的所有歌词做整合
def format_all_lrc():
    os.chdir('/Users/yinchenhao/Documents/lrc/temp')
    file_list = os.listdir('/Users/yinchenhao/Documents/lrc/temp')
    for file in file_list:
        if file.find('-') == -1:
            print(file)
            new_singer_file = open('/Users/yinchenhao/Documents/lrc/singer/' + file,'a',encoding='utf-8')
            file_content = open(file, 'r')
            singer_content = file_content.read()
            new_singer_content = format_content(singer_content)
            new_singer_file.write(new_singer_content)
            file_content.close()
            new_singer_file.close()







