# cloudMusic-analyse
基于网易云的歌词数据可视化和分析

本项目是受到了一篇《我用Python分析了42万字的歌词，为了搞清楚民谣歌手们在唱些什么》的启发而做的，在原文中作者只是给出了分析后的数据，并没有给出代码和实现过程。于是我自己根据这个创意实现了大部分的内容，并加入了一些新的东西。


这是一个网易云音乐的歌词数据分析与可视化项目。我主要做了三个方面的工作：
(1)用爬虫爬取网易云的歌词
(2)对歌词进行数据分析
(3)数据可视化


## 歌词数据爬取
网易云的所有歌曲都是以id的形式在url上显示呈现，所以只需要找到歌曲的id，再通过解析就可以获取。我将爬取的歌词文件存入了data文件夹。

![歌词文件形式](https://github.com/adrainYin/cloudMusic-analyse/raw/master/png/lrc.png)

## 歌词数据分析与可视化

歌词的分词我使用了jieba分析工具，情感分析我使用了ntusd情感词典和百度AI开放平台的情感倾向分析工具。
在数据可视化方面我使用了pyecharts这个开放类库，仅仅需要几行代码就可以将结果可视化出来。
具体的内容请看：

(1)歌手们主要唱了什么:
![歌手们主要唱了什么](https://github.com/adrainYin/cloudMusic-analyse/raw/master/png/all_lrc_analyse.png)
  
  
(2)歌手最喜欢的季节：
![歌手们最喜欢的季节](https://github.com/adrainYin/cloudMusic-analyse/raw/master/png/season.png)
  
  
(3)歌手们的情感倾向:
![歌手的感情倾向](https://github.com/adrainYin/cloudMusic-analyse/raw/master/png/pos_baiduAI.png)
![歌手的感情倾向](https://github.com/adrainYin/cloudMusic-analyse/raw/master/png/pos_ntusd.png)
  
  
(4)赵雷的歌曲中主要有哪些正面情感和负面情感:
![赵雷](https://github.com/adrainYin/cloudMusic-analyse/raw/master/png/zhaolei_analyse.png)
  
  
(5)做了一个赵雷的词云:
![赵雷](https://github.com/adrainYin/cloudMusic-analyse/raw/master/png/zhaolei_wordcloud.png)

## 如何使用

(1)直接可以打开results中的.html文件，观察可视化内容。

(2)我们提供了输入指定歌手名来制作词云和歌手词频可视化：
    1.  制作歌手词频可视化：plot_singer_chart() 参数为歌手名 
    2. 制作词云可视化：make_wordcloud_by_singer_frequency() 参数为歌手名
