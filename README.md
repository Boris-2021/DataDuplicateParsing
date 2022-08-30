# DataDuplicateParsing
# 解析文本相似的重复数据


使用方式：
在DataTool目录下使用CMD命令行操作使用文本聚类工具。

原始数据：
data文件夹中放入原始数据。

要求原始数据中必须有这5列：[aclineid, volt, i_node, j_node]


使用实例：
命令行：python datahandle_jieba.py -f data/data.xlsx -t 0.8
参数说明：-f 原始文件路径，-t 选择聚类的相似度阈值

等待进度条完成100%，生成新的文件。



两个模式
datahandle_jieba.py
表示数据被jieba分词后聚类

jiebaDict.txt文件时结巴分词字典，丰富这个文件的词汇，可以增强分词的效果。

datahandle_re.py
表示数据正则处理后聚类。
线段名称分词长度为8规则大致为：来源，线路名称，ID，线路名称，线，分隔符，线路类型，分隔符。
场站分词长度5：省，市，站，第一个数字，第二个数字。
