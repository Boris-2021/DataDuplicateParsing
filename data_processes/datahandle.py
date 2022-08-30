# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :datahandle.py
# @Time      :2022/8/17 14:13
# @Author    :Boris_zhang
import pandas as pd
import numpy as np
import getopt
import sys

# 读oms/ems 数据
def read_excel(patn):
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
            sim_score = SimSeq2Str(df_list[start], df_list[i])
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
        # print(cluster_list)
        # 簇ID加1
        clusterId += 1
        # print("*" * 80)

    # cluster_list转成DataFrame格式
    cluster_list_df = pd.DataFrame(cluster_list,columns=['aclineid', 'name', 'i_node', 'j_node', 'volt', 'clusterId', 'sim_score'])
    # cluster_list_df.to_csv('cluster_list_df.csv', index=False)


def SimSeq2Weight(list1, list2):
    '''
    计算两个列表“综合”的相似度
    'name'：0.5权重, 'i_node'：0.2权重, 'j_node'：0.2权重, 'volF'：0.1权重
    :param list1:
    :param list2:
    :return:
    '''
    sim_score_list = []
    for seqA, seqB in zip(list1[1:], list2[1:]):
        sim_score = jaccard_similarity(seqA, seqB)
        sim_score_list.append(sim_score)

    # 计算综合相似度
    sim_score = sim_score_list[0] * 0.5 + sim_score_list[1] * 0.2 + sim_score_list[2] * 0.2 + sim_score_list[3] * 0.1
    return sim_score


def SimSeq2Str(list1, list2):
    '''
    计算两个列表转化为str计算的相似度，更直接直观。
    :param list1:
    :param list2:
    :return:
    '''
    # 将list[-1]转化为str
    list1[-1], list2[-1] = str(list1[-1]), str(list2[-1])
    seq1, seq2 = ''.join(list1[1:]), ''.join(list2[1:])
    sim_score = jaccard_similarity(seq1, seq2)
    return sim_score


# Jaccard 相似度
def jaccard_similarity(s1, s2):
    if type(s1) != str:
        return int(s1 == s2)
    s1, s2 = set(s1), set(s2)
    score = len(s1 & s2) / len(s1 | s2)
    # score保留两位小数
    score = round(score, 2)
    return score


# 写入追加写入记事本功能
def write_append(file_name, content):
    with open(file_name, 'a') as f:
        f.write(content)
        f.write('\n')


def Station_info(df):
    '''
    这是从OMS提取场站信息的方法
    :param df:
    :return:
    '''
    province_dic = {'北京市': 11, '天津市': 12, '上海市': 31, '重庆市': 50, '河北省': 13, '河南省': 41, '云南省': 53,
                    '辽宁省': 21, '黑龙江省': 23, '湖南省': 43, '安徽省': 34, '山东省': 37, '新疆维吾尔': 65, '江苏省': 32,
                    '浙江省': 33, '江西省': 36, '湖北省': 42, '广西壮族': 45, '甘肃省': 62, '山西省': 14, '内蒙古': 15,
                    '陕西省': 61, '吉林省': 22, '福建省': 35, '贵州省': 52, '广东省': 44, '青海省': 63, '西藏': 54,
                    '四川省': 51, '宁夏回族': 64, '海南省': 46}

    StationDf = pd.DataFrame(columns=["ID", "CODE", "NAME", "TYPE", "VOLTAGE_TYPE", "CROSS_PROVINCE", "CARBON_FACTOR"])

    print(df.columns)

    for tup in df.iterrows():  # iterrows()  itertuples
        # print(tup[1], type(tup))
        print(tup[1]['volF'])  # , type(tup)
        break


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

    percentage = round(finish_tasks_number / tasks_number * 100)
    print("\r进度: {}%: ".format(percentage), "▓" * (percentage // 2), end="")
    sys.stdout.flush()


if __name__ == "__main__":
    file_name, threshold = main_input(sys.argv[1:])
    df_list = read_excel(file_name)
    scan_list(df_list, threshold)

    '''
    df_list = read_excel("../O.xlsx")
    scan_list(df_list)

    '''

    pass
