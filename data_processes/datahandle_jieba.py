# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :datahandle_jieba.py
# @Time      :2022/8/19 12:53
# @Author    :Boris_zhang

import pandas as pd
import numpy as np
import jieba
import getopt
import sys

# jieba添加字典
jieba.load_userdict("jiebaDict.txt")


# 读oms/ems 数据
def read_excel_jieba(patn):
    '''
    加载文件数据并输出处理好的数据
    :param patn:
    :return:
    '''
    df = pd.read_excel(patn, index_col=False)
    '''数据初步的清洗处理'''
    # 表头去掉左右空格
    df.columns = df.columns.str.strip()
    # print(df.info())
    # print(len(df))
    # 去掉空行
    df = df.dropna(how='all')
    # 去掉重复行
    df = df.drop_duplicates()
    # 去掉i_node 和 j_node 元素重复的行
    df = df.drop_duplicates(subset=['i_node', 'j_node'])

    # print(len(df))
    # apply 去掉i_node 和 j_node 最后的数字 去掉左右空格
    # df['i_node'] = df['i_node'].apply(lambda x: ".".join(x.split('.')[:-2]).strip())
    # df['j_node'] = df['j_node'].apply(lambda x: ".".join(x.split('.')[:-2]).strip())
    df['i_node'] = df['i_node'].apply(lambda x: x.strip())
    df['j_node'] = df['j_node'].apply(lambda x: x.strip())
    # aclineid,name,去掉左右空格
    df['aclineid'] = df['aclineid'].apply(lambda x: x.strip())
    df['name'] = df['name'].apply(lambda x: x.strip())
    # 取出 aclineid，name，i_node，j_node，volF
    df = df[['aclineid', 'name', 'i_node', 'j_node', 'volt']]
    # df["name"]使用apply,分词化列表
    df["name"] = df["name"].apply(lambda x: jieba.lcut(x))

    # # 添加一列计数
    # df["name_cont"] = df["name"].apply(lambda x: len(x))

    # df['i_node']按.分割
    df['i_node'] = df['i_node'].apply(lambda x: x.split('.'))
    # df['j_node']按.分割
    df['j_node'] = df['j_node'].apply(lambda x: x.split('.'))

    # df.to_csv("分词后数据.csv", index=False)

    # 将df内容提取成列表
    df_list = df.values.tolist()
    # print(df_list)
    return df_list


def scan_list(df_list, threshold=0.8):
    '''
    扫描数据列表，提取相似簇的数据
    :param df_list:
    :return:
    '''
    total_len = len(df_list)
    # 初始化一个簇聚类空列表
    cluster_list = []
    clusterId = 0

    while df_list:
        start = 0
        # 添加簇首元素
        new_cluster_first_element = df_list[start].copy()
        # 添加簇首元素的簇ID
        new_cluster_first_element.append(clusterId)
        # 添加簇首元素的相似度
        new_cluster_first_element.append(1.00)
        # 添加簇首元素到簇聚类列表
        cluster_list.append(new_cluster_first_element)
        # print(new_cluster_first_element)

        '''new_cluster_first_element追加写入res.txt'''
        # write_append('res.txt', str(new_cluster_first_element))

        # 初始化记录删除元素索引的列表
        del_index_list = [start]
        # clusterId变量向下兼容
        clusterId = clusterId
        # print(len(df_list))
        for i in range(1, len(df_list)):
            # print(i)
            # print(df_list[start])
            # print(df_list[i])
            sim_score = SimSeq2set(df_list[start], df_list[i])
            if sim_score >= float(threshold):
                # 如果相似度大于0.5，则添加到簇中
                new_cluster_element = df_list[i].copy()
                # 添加簇元素的簇ID
                new_cluster_element.append(clusterId)
                # 添加簇元素的相似度
                new_cluster_element.append(sim_score)
                cluster_list.append(new_cluster_element)
                # 将当前元素的索引添加到删除列表中
                del_index_list.append(i)

                '''new_cluster_element追加写入res.txt'''
                # write_append('res.txt', str(new_cluster_element))

        # print(del_index_list)
        # 删除已经添加到簇中的元素
        df_list = np.delete(df_list, del_index_list, axis=0).tolist()
        # print(type(df_list))
        now_len = len(df_list)
        # 展示进度
        progress_bar(total_len-now_len, total_len)
        # 簇ID加1
        clusterId += 1
        # print("*" * 80)

    # cluster_list转成DataFrame格式
    cluster_list_df = pd.DataFrame(cluster_list,
                                   columns=['aclineid', 'name', 'i_node', 'j_node', 'volt', 'clusterId', 'sim_score'])
    # cluster_list_df["name_org"] 拼接回来
    cluster_list_df["name_org"] = cluster_list_df["name"].apply(lambda x: "".join(x))
    # cluster_list_df["i_node_org"] 拼接回来
    cluster_list_df["i_node_org"] = cluster_list_df["i_node"].apply(lambda x: ".".join(x))
    # cluster_list_df["j_node_org"] 拼接回来
    cluster_list_df["j_node_org"] = cluster_list_df["j_node"].apply(lambda x: ".".join(x))
    # 字段顺序调整
    cluster_list_df = cluster_list_df[
        ['aclineid', 'name', 'name_org', 'i_node', 'i_node_org', 'j_node', 'j_node_org', 'volt', 'clusterId',
         'sim_score']]

    cluster_list_df.to_csv('cluster_list_df_jieba.csv', index=False)


def SimSeq2set(list1, list2):
    '''
    计算两个列表转化为str计算的相似度，更直接直观。
    :param list1:
    :param list2:
    :return:
    '''
    # 将list[-1]转化为str
    list1[-1], list2[-1] = str(list1[-1]), str(list2[-1])
    # list1[1:]展开成一维
    seq1, seq2 = [i for arr in list1[1:] for i in arr], [i for arr in list2[1:] for i in arr]

    sim_score = jaccard_similarity(seq1, seq2)
    # print(seq1, seq2)
    return sim_score


# Jaccard 相似度
def jaccard_similarity(s1, s2):
    s1, s2 = set(s1), set(s2)
    # print(s1, s2)
    score = len(s1 & s2) / len(s1 | s2)
    # score保留两位小数
    score = round(score, 2)
    # print(score)
    return score


# 写入追加写入记事本功能
def write_append(file_name, content):
    with open(file_name, 'a') as f:
        f.write(content)
        f.write('\n')


def main_input(argv):
    try:
        options, args = getopt.getopt(argv, "hf:t:", ["help", "file=", "threshold="])
    except getopt.GetoptError:
        sys.exit()
    file_name, threshold = None, None
    for option, value in options:
        if option in ("-h", "--help"):
            print("入参：-f 文件路径 -t 阈值 \n 例如：python3 demo_zhang.py -f /home/oms/oms_data/oms_data.xlsx -t 0.8")
        if option in ("-f", "--file"):
            print("file is: {0}".format(value))
            file_name = value
        if option in ("-t", "--threshold"):
            print("threshold is: {0}".format(value))
            threshold = value

    if file_name and threshold:
        return file_name, threshold
    else:
        print("error args: {0}".format(args))
        return None, None

# 展示进度
def progress_bar(finish_tasks_number, tasks_number):
    """
    进度条

    :param finish_tasks_number: int, 已完成的任务数
    :param tasks_number: int, 总的任务数
    :return:
    """

    percentage = round(float(finish_tasks_number / tasks_number * 100), 1)
    print("\r进度: {}%: ".format(percentage), "▓" * (int(percentage) // 2), end="")
    sys.stdout.flush()

if __name__ == "__main__":
    file_name, threshold = main_input(sys.argv[1:])
    df_list = read_excel_jieba(file_name)
    scan_list(df_list, threshold)

    '''
    df_list = read_excel_jieba("../浙江全量线路OMS.xlsx")
    # scan_list(df_list)
    '''

