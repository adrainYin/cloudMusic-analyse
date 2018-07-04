import re
import os
import jieba
from pyecharts import Bar, Pie
from pyecharts import WordCloud
from collections import Counter
import operator

# 对歌词文本做粗处理，并且删除作词作曲等信息
# 传入的参数是对文本文件的直接读取
def format_content(content):
    content = content.replace(u'\xa0', u' ')
    content = re.sub(r'\[.*?\]','',content)
    content = re.sub(r'\s*作曲.*\n','',content)
    content = re.sub(r'\s*作词.*\n','',content)
    content = re.sub(r'.*:','',content)
    content = re.sub(r'.*：','',content)
    content = content.replace('\n', ' ')
    return content

# 分词，用停止词汇表分词，最后返回词汇列表
def word_segmentation(content, stop_words):

    # 使用 jieba 分词对文本进行分词处理
    jieba.enable_parallel()
    seg_list = jieba.cut(content, cut_all=False)

    seg_list = list(seg_list)

    # 去除停用词
    word_list = []
    for word in seg_list:
        if word not in stop_words:
            word_list.append(word)

    # 过滤遗漏词、空格
    user_dict = [' ', '哒']
    filter_space = lambda w: w not in user_dict
    word_list = list(filter(filter_space, word_list))

    return word_list

#读取停止词汇表
def read_stopWords():
    stopWordsFile = open('/Users/yinchenhao/Documents/lrc/stop_words.txt','r')
    stop_word_list = stopWordsFile.read().split('\n')
    stopWordsFile.close()
    return stop_word_list

# 读取情感词典，为之后的数据情感分析做准备
def read_ntusd_emotion():
    positive_words_file = open('/Users/yinchenhao/Documents/lrc/emotion-dict/ntusd-positive.txt','r')
    positive_words = positive_words_file.read().split('\n')
    negative_words_file = open('/Users/yinchenhao/Documents/lrc/emotion-dict/ntusd-negative.txt','r')
    negative_words = negative_words_file.read().split('\n')
    positive_words_file.close()
    negative_words_file.close()
    return positive_words, negative_words

def analyse_singer_Lrc(singerame):
    curr_singer_file = ''
    for file in os.listdir('/Users/yinchenhao/Documents/lrc/singer/'):
        if file.find(singerame) != -1:
            curr_singer_file = file
            break
    if curr_singer_file != '':
        singer_name = curr_singer_file.split('.')[0]
        songs_file = open('/Users/yinchenhao/Documents/lrc/singer/' + curr_singer_file,'r')
        content = songs_file.read()
        songs_file.close()
        #歌手的歌词内容
        #content = format_content(content)
        #停止词汇表
        stop_words = read_stopWords()
        #情感词典
        positive_words, negative_words = read_ntusd_emotion()
        word_list = word_segmentation(content, stop_words)
        frequency = word_frequency(word_list)
        frequency_dict = {}
        for item in frequency:
            frequency_dict[item[0]] = item[1]
        words = [item[0] for item in frequency]
        pos_dict = {}
        neg_dict = {}
        total_pos = 0
        total_neg = 0
        for word in words:
            if word in positive_words:
                pos_dict[word] = frequency_dict[word]
                total_pos += frequency_dict[word]
            if word in negative_words:
                neg_dict[word] = frequency_dict[word]
                total_neg += frequency_dict[word]
        return singer_name, pos_dict, neg_dict, total_pos, total_neg
    else:
        print('查找的歌手不存在')
        return

def plot_singer_chart(singername,*topN):
    singer_name, pos_dict, neg_dict, total_pos, total_neg = analyse_singer_Lrc(singername)

    sorted_pos_dict = sorted(pos_dict.items(), key=operator.itemgetter(1), reverse=True)
    sorted_neg_dict = sorted(neg_dict.items(), key=operator.itemgetter(1), reverse=True)
    #print(sorted_pos_dict)
    #print(sorted_neg_dict)
    if topN:
        pos_items = [item[0] for item in sorted_pos_dict][0:topN[0]]
        pos_values = [item[1] for item in sorted_pos_dict][0:topN[0]]
        neg_items = [item[0] for item in sorted_neg_dict][0:topN[0]]
        neg_values = [item[1] for item in sorted_neg_dict][0:topN[0]]
    else:
        pos_items = [item[0] for item in sorted_pos_dict][0:10]
        pos_values = [item[1] for item in sorted_pos_dict][0:10]
        neg_items = [item[0] for item in sorted_neg_dict][0:10]
        neg_values = [item[1] for item in sorted_neg_dict][0:10]

    chart = Pie(singer_name ,title_pos='center')
    chart.add('正面',pos_items, pos_values,center=[25,50],legend_top=30,is_more_utils=True)
    chart.add('负面',neg_items, neg_values, center=[75,50],legend_top=30,is_more_utils=True)
    chart.render()


# 根据歌手的词频制作词云
def make_wordcloud_by_singer_frequency(singername):
    curr_singer_file = ''
    for file in os.listdir('/Users/yinchenhao/Documents/lrc/singer/'):
        if file.find(singername) != -1:
            curr_singer_file = file
            break
    if curr_singer_file != '':
        singer_name = curr_singer_file.split('.')[0]
        songs_file = open('/Users/yinchenhao/Documents/lrc/singer/' + curr_singer_file, 'r')
        content = songs_file.read()
        songs_file.close()
        stop_words = read_stopWords()
        word_list = word_segmentation(content, stop_words)
        counter = word_frequency(word_list)
        frequency_dict = {}
        for item in counter:
            frequency_dict[item[0]] = item[1]
        sorted_frequency_dict = sorted(frequency_dict.items(), key=operator.itemgetter(1), reverse=True)
        items = [item[0] for item in sorted_frequency_dict]
        values = [item[1] for item in sorted_frequency_dict]
        print(sorted_frequency_dict)
        wordcloud = WordCloud(singer_name + '的词云',width=1300, height=620, title_pos='center')
        wordcloud.add("", items, values, word_size_range=[20, 100])
        wordcloud.render()
    else:
        print('歌手不存在')


# 分析歌手们最喜爱的季节
def analyse_season():
    file = open('/Users/yinchenhao/Documents/lrc/all_lrc.txt', 'r')
    content = file.read()
    file.close()
    stop_list = read_stopWords()
    word_list = word_segmentation(content, stop_list)
    counter = word_frequency(word_list)
    frequency_dict = {}
    for item in counter:
        frequency_dict[item[0]] = item[1]
    season_dict = {'春':0,'夏':0,'秋':0,'冬':0}
    #统计后的所有词汇表
    word_list = [item[0] for item in counter]
    for word in word_list:
        if word.find('春') != -1:
            season_dict['春'] += frequency_dict[word]
        elif word.find('夏') != -1:
            season_dict['夏'] += frequency_dict[word]
        elif word.find('秋') != -1:
            season_dict['秋'] += frequency_dict[word]
        elif word.find('冬') != -1:
            season_dict['冬'] += frequency_dict[word]
    print(season_dict)
    items = ['春','夏','秋','冬']
    values = [season_dict['春'], season_dict['夏'],season_dict['秋'],season_dict['冬']]
    chart = Pie('歌手们最喜欢的季节', title_pos='left')
    chart.add('季节',items, values, center=[50,50])
    chart.render()

#分析歌手最喜欢的时间
def analyse_time():
    time_dict = {'昨天':0, '今天':0, '明天':0}
    file = open('/Users/yinchenhao/Documents/lrc/all_lrc.txt', 'r')
    content = file.read()
    file.close()
    stop_list = read_stopWords()
    #使用停止词表得到有重复的所有词
    word_list = word_segmentation(content, stop_list)
    counter = word_frequency(word_list)
    frequency_dict = {}
    for item in counter:
        frequency_dict[item[0]] = item[1]
    for key in frequency_dict:
        if key.find('昨天') != -1:
            time_dict['昨天'] += frequency_dict[key]
        elif key.find('今天') != -1:
            time_dict['今天'] += frequency_dict[key]
        elif key.find('明天') != -1:
            time_dict['明天'] += frequency_dict[key]
    #print(time_dict)
    items = ['昨天', '今天', '明天']
    values = [time_dict['昨天'], time_dict['今天'], time_dict['明天']]
    chart = Pie('歌手们最喜欢活在哪一天', title_pos='left')
    chart.add('时间', items, values, center=[50, 50])
    chart.render()

# 词频统计
# 返回前 top_N 个值，如果不指定则返回所有值
# 返回类型是字典
def word_frequency(word_list):
    counter = Counter(word_list).most_common()
    return counter

#对统计后的进行可视化
def plot_chart(*topN):
    file = open('/Users/yinchenhao/Documents/lrc/all_lrc.txt', 'r')
    content = file.read()
    file.close()
    stop_list = read_stopWords()
    word_list = word_segmentation(content, stop_list)
    counter = word_frequency(word_list)
    if topN:
        items = [item[0] for item in counter][0:topN[0]]
        values = [item[1] for item in counter][0:topN[0]]
    else:
        items = [item[0] for item in counter][0:20]
        values = [item[1] for item in counter][0:20]
    chart = Pie()
    chart.add('词频', items, values, is_label_show=True, is_more_utils=True)
    chart.show_config()
    chart.render()

#对所有歌手的情感数据做分析，返回情感指数列表
def analyse_all_emotion_by_emotiondict():
    stop_words = read_stopWords()
    positive_words, negative_words = read_ntusd_emotion()
    file_list = os.listdir('/Users/yinchenhao/Documents/lrc/singer/')
    all_singer_emotion = {}
    for file in file_list:
        if file.find('.txt') != -1:
            singer_name = file.split('.')[0]
            file_IO = open('/Users/yinchenhao/Documents/lrc/singer/' + file,'r')
            content = file_IO.read()
            file_IO.close()
            #有重复的词汇列表
            word_list = word_segmentation(content, stop_words)
            counter = word_frequency(word_list)
            frequency_dict = {}
            total_pos = 0
            total_neg = 0
            for item in counter:
                frequency_dict[item[0]] = item[1]
            #没有重复的词汇列表
            word_list = [item[0] for item in counter]
            for word in word_list:
                if word in positive_words:
                    total_pos += frequency_dict[word]
                if word in negative_words:
                    total_neg += frequency_dict[word]
            pos_index = round(total_pos / (total_pos + total_neg) * 100 , 1)
            all_singer_emotion[singer_name] = pos_index
            print(singer_name + '分析完成')
        else:
            print(file + '不是歌词文件')
    return all_singer_emotion

# 可视化基于ntusd情感词典分类的所有歌手正面指数的排名
def plot_pos_emotion(*topN):
    emotion_dict = analyse_all_emotion_by_emotiondict()
    sorted_emotion_dict = sorted(emotion_dict.items(), key=operator.itemgetter(1), reverse=True)
    if topN:
        items = [item[0] for item in sorted_emotion_dict][0:topN[0]]
        values = [item[1] for item in sorted_emotion_dict][0:topN[0]]
    else:
        items = [item[0] for item in sorted_emotion_dict]
        values = [item[1]for item in sorted_emotion_dict]

    chart = Bar('歌手正面情感分析-ntusd情感词典')
    chart.add('正面情感指数(数值越高歌手的歌词越积极向上)', items, values, is_more_utils=True)
    chart.show_config()
    chart.render()

# 可视化基于ntusd情感词典分类的所有歌手负面指数的排名
def plot_neg_emotion(*topN):
    emotion_dict = analyse_all_emotion_by_emotiondict()
    for key in emotion_dict:
        emotion_dict[key] = 100 - emotion_dict[key]
    sorted_emotion_dict = sorted(emotion_dict.items(), key=operator.itemgetter(1), reverse=True)
    if topN:
        items = [item[0] for item in sorted_emotion_dict][0:topN[0]]
        values = [item[1] for item in sorted_emotion_dict][0:topN[0]]
    else:
        items = [item[0] for item in sorted_emotion_dict]
        values = [item[1]for item in sorted_emotion_dict]

    chart = Bar('歌手负面情感分析-ntusd情感词典')
    chart.add('负面情感指数(数值越高歌手的歌词越沉重阴暗)', items, values, is_more_utils=True)
    chart.show_config()
    chart.render()
