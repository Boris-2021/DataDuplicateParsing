# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :link_db.py
# @Time      :2022/8/29 11:22
# @Author    :Boris_zhang
import pandas as pd
import numpy as np
# import pymysql
import sqlalchemy

# 连接数据库demo, 读line_info表
def connect_db():
    # 创建连接
    conn = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/demo')
    # pandas读line_info表
    df = pd.read_sql('select LINE_ID, LINE_NAME, LINE_VL, START_DOT_ID, END_DOT_ID from line_info', conn)
    print(df.columns)
    df.to_csv("数据库去重info.csv", index=False)



def read_csv():
    # 读数据去重info.csv
    df_RD = pd.read_csv("数据库去重info.csv", index_col=False)
    # print(len(df_RD))
    # apply 去掉'LINE_NAME',去掉左右空格
    df_RD['LINE_NAME'] = df_RD['LINE_NAME'].apply(lambda x: x.strip())
    # 按LINE_NAME 列重复的去重
    # df_RD = df_RD.drop_duplicates(subset=['LINE_NAME'])
    # print(len(df_RD))
    # print(len(df_RD))

    # 读算法去重数据
    df_ALG = pd.read_csv("data_processes/统计个数后re.csv", index_col=False)
    # print(df_ALG.columns)
    print(len(df_ALG))

    # df_RD按照LINE_NAME 左连接 df_ALG 按照 name_org
    df_RD_ALG = pd.merge(df_ALG, df_RD, left_on='name_org', right_on='LINE_NAME', how='outer')
    # print(df_RD_ALG.columns)
    # print(df_RD_ALG)
    # 取name_org, i_node_org, j_node_org, clusterId, sim_score, count, LINE_NAME, LINE_VL 列
    df_RD_ALG = df_RD_ALG[['name_org', 'i_node_org', 'j_node_org', 'clusterId', 'sim_score', 'count', 'LINE_NAME', 'LINE_VL']]

    df_RD_ALG.to_csv("去重合并re.csv", index=False)


# 读去重合并.csv
def read_csv2():
    df = pd.read_csv("去重合并.csv", index_col=False)
    # 查name_org列的空值个数
    print(df['name_org'].isnull().sum())
    # print(df.columns)
    # print(df)


if __name__ == "__main__":
    read_csv()
    # read_csv2()
    pass
