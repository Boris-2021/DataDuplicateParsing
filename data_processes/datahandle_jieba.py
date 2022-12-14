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
            # break

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
        # break

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
    list1_1, list2_2 = str(list1[-1]), str(list2[-1])
    # print(list1,list2)
    # 判断线段名称是否存在  省.地名 ,且出入场站不包含“虚拟”这种情况
    if "." in list1[1] or "." in list2[1]:
        node_out_in = "".join(list1[2]+list1[3]+list2[2]+list2[3])  # 判断出入场站有没有“虚拟”
        if "虚拟" not in node_out_in:
            line1 = "".join(list1[1])
            line2 = "".join(list2[1])
            # print(line1, line2)
            # 如果.在字符串中删除.之前的内容
            line1 = line1.split(".")[1] if "." in line1 else line1
            line2 = line2.split(".")[1] if "." in line2 else line2

            if line1 == line2: # 线路去除省之后相同，名称相同基本认定为同线路，不需要继续判断。
                sim_score = 0.99
                return sim_score

    # list1[1:]展开成一维
    seq1, seq2 = [i for arr in list1[1:-1] for i in arr], [i for arr in list2[1:-1] for i in arr]
    seq1.append(list1_1)
    seq2.append(list2_2)
    # print(seq1, seq2)
    sim_score = jaccard_similarity(seq1, seq2)
    # 在以上的基础上，如果出场站都是虚拟站，进一步削弱评分
    if "虚拟" in seq2[-4] and seq2[-4]==seq1[-4]:
        # 出场站都是虚拟站，削弱评分
        if seq2[-7] != seq1[-7]:  # 入场站又不同基本不是同线路，评分直接砍0.5以下。
            sim_score = sim_score-0.50
        sim_score = sim_score-0.05

    return sim_score


# Jaccard 相似度
def jaccard_similarity(s1, s2):
    s1, s2 = set(s1), set(s2)
    s3 = s1 & s2
    s4 = s1 | s2
    # 统计两个都有虚拟情况，进行得分削减
    count_ = 0
    for i in s3:
        if "虚拟" in i:
            count_+=1

    # 集合中去除虚拟场站元素的计算 / 分子去除计算
    # score = (len(s3) - count_) / (len(s4)-count_)
    score = (len(s3) - count_) / len(s4)

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




    # s1 = {'仙门', '1272', '五丰', 'T接线', '丽水', '五丰变', '115', '2', 'ls', '虚拟', '9'}
    # s2 = {'仙门', '1272', '雁门', 'T接线', '丽水', '雁门变', '115', '2', 'ls', '虚拟', '9'}