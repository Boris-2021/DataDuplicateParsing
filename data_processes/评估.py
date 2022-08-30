# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :评估.py
# @Time      :2022/8/24 14:49
# @Author    :Boris_zhang

import pandas as pd
import numpy as np
import sys


# 读处理后 数据
def read_csv(patn):
    '''
    加载文件数据并输出处理好的数据
    :param patn:
    :return:
    '''
    df = pd.read_csv(patn, index_col=False)
    '''数据初步的清洗处理'''
    # 添加一列[count]是[clusterId]内容的出现次数统计个数
    df["count"] = df["clusterId"].apply(lambda x: df["clusterId"].value_counts()[x])
    # print(df['count'])
    df.to_csv("统计个数后jieba.csv", index=False)


if __name__ == "__main__":
    read_csv("cluster_list_df_jieba.csv")
    pass
