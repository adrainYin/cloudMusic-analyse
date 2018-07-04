import urllib.request
import json
import requests
import os
import re
import  jieba
import operator
from pyecharts import Bar, Pie

import download_lrc

def get_access_token():
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=UW2BgwYmGaRSWBPMQkcd8zHf&client_secret=4CqvIpHG0qaKtZxaAh0uDzeHftOnGxnR'
    request = urllib.request.Request(host)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    response = urllib.request.urlopen(request)
    content = response.read()
    content = json.loads(content)
    if (content):
        return (content["access_token"])

#歌词调用百度API进行情感分析
def get_emotion_analyse_content(text):
    # file = open('/Users/yinchenhao/Documents/lrc/singer/all_lrc.txt')
    # file = open('/Users/yinchenhao/Documents/lrc/singer/守麦.txt')
    access_token = get_access_token().strip()
    url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?access_token='+ access_token
    headers = {"Content-Type": "application/json"}
    data = {"text": text}
    #将dat封装成json的格式
    data = json.dumps(data).encode('gbk')
    #调用api后返回的情感分类数据
    r = requests.post(url, data=data, headers=headers)
    return r.text

#格式化分析后的数据
def format_emotion_data(text):
    emotion_list = re.match('.*"positive_prob": (.*?),.*"negative_prob": (.*?),.*"sentiment": (.*?)}.*',text)
    pos_str = 'positive_prob=' + emotion_list.group(1)
    neg_str = 'negative_prob=' + emotion_list.group(2)
    sen_str = 'sentiment=' + emotion_list.group(3)
    return pos_str + ' ' + neg_str + ' ' + sen_str + '\n'


# 对百度API返回的每首歌的情感分析做数据处理，并将所有的分析数据写入文件，方便之后的处理
def analyse_emotion_by_baiduAPI():
    file_list = os.listdir('/Users/yinchenhao/Documents/lrc/temp/')
    os.chdir('/Users/yinchenhao/Documents/lrc/temp/')
    for file in file_list:
        if file.find('-') != -1:
            singer_name_str = file.split('-')[0]
            song_name_str = file.split('-')[1].split('.')[0]
            print(file)
            file_io = open(file,'r')
            content = file_io.read()
            file_io.close()
            content = re.sub('[^\u4e00-\u9fa5]','',content)
            if content == '':
                print('该歌词中不含有中文字符!')

            else:
                text = get_emotion_analyse_content(content[0:1024])
                emotion_data = format_emotion_data(text)
                print(emotion_data)
                print('***********************')
                singer_name_file = open('/Users/yinchenhao/Documents/lrc/singer/' + singer_name_str + '-emotion.txt', 'a')
                singer_name_file.write(emotion_data)
                print(song_name_str + '情感分析完成')
                singer_name_file.close()


# 删除所有的空歌词文件，因为如果歌词文件为空，那么在分析时候就会报错
def delete_all_empty_file():
    os.chdir('/Users/yinchenhao/Documents/lrc/temp/')
    file_list = os.listdir('/Users/yinchenhao/Documents/lrc/temp/')
    for file in file_list:
        file_size = os.path.getsize(file)
        if file_size == 0:
            os.remove('/Users/yinchenhao/Documents/lrc/temp/' + file)

#分析歌手们的正面歌词情感，并做出排名并可视化
def analy_singer_pos_emotion():
    file_list = os.listdir('/Users/yinchenhao/Documents/lrc/singer_emotion/')
    emotion_dict = {}
    for file in file_list:
        total_prob = 0
        count = 0
        singer_name = file.split('-')[0]
        open_file = open('/Users/yinchenhao/Documents/lrc/singer_emotion/' + file,'r')
        for emotion_line in open_file.readlines():
            emotion_line = emotion_line.strip()
            positive_prob = re.match('positive_prob=(.*?) .*',emotion_line).group(1)
            total_prob += float(positive_prob)
            count += 1
        total_pos_prob = round(total_prob / count, 3)
        emotion_dict[singer_name] = total_pos_prob
    print(emotion_dict)
    return emotion_dict

#分析歌手们的负面歌词情感，并做出排名并可视化
def analy_singer_neg_emotion():
    file_list = os.listdir('/Users/yinchenhao/Documents/lrc/singer_emotion/')
    emotion_dict = {}
    for file in file_list:
        total_prob = 0
        count = 0
        singer_name = file.split('-')[0]
        open_file = open('/Users/yinchenhao/Documents/lrc/singer_emotion/' + file,'r')
        for emotion_line in open_file.readlines():
            emotion_line = emotion_line.strip()
            negative_prob = re.match('.*?negative_prob=(.*?) .*',emotion_line).group(1)
            total_prob += float(negative_prob)
            count += 1
        total_neg_prob = round(total_prob / count, 3)
        emotion_dict[singer_name] = total_neg_prob
    print(emotion_dict)
    return emotion_dict

# 对歌手的正面情感数据做可视化和排名
def plot_singer_pos_emotion_chart(*topN):
    emotion_dict = analy_singer_pos_emotion()
    sorted_emotion_dict = sorted(emotion_dict.items(), key = operator.itemgetter(1), reverse = True)
    if topN:
        items = [item[0] for item in sorted_emotion_dict][0:topN[0]]
        values = [round(item[1] * 100, 1) for item in sorted_emotion_dict][0:topN[0]]
    else:
        items = [item[0] for item in sorted_emotion_dict]
        values = [round(item[1]*100,1) for item in sorted_emotion_dict]

    chart = Bar('歌手正面情感分析-百度AI')
    chart.add('正面情感指数(数值越高歌手的歌词越积极向上)', items, values, is_more_utils=True)
    chart.show_config()
    chart.render()

# 对歌手的负面情感数据做可视化和排名
def plot_singer_neg_emotion_chart(*topN):
    emotion_dict = analy_singer_neg_emotion()
    sorted_emotion_dict = sorted(emotion_dict.items(), key = operator.itemgetter(1), reverse = True)
    if topN:
        items = [item[0] for item in sorted_emotion_dict][0:topN[0]]
        values = [round(item[1] * 100, 1) for item in sorted_emotion_dict][0:topN[0]]
    else:
        items = [item[0] for item in sorted_emotion_dict]
        values = [round(item[1]*100,1) for item in sorted_emotion_dict]

    print(items)
    print(values)
    chart = Bar('歌手负面情感分析-百度AI')
    chart.add('负面情感指数(数值越高歌手的歌词越沉重阴暗)', items, values, is_more_utils=True)
    chart.show_config()
    chart.render()
