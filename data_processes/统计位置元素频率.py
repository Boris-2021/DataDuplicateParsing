# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :统计位置元素频率.py
# @Time      :2022/9/5 10:49
# @Author    :Boris_zhang
import numpy as np
import pandas as pd

# 读取数据
def read_data(path):
    df = pd.read_csv(path, index_col=False)
    # print(df)
    # print(df.columns)
    # 取出name_cut列的内容
    res = df['name_cut'].values.tolist()
    # 总长度
    tatal_len = len(res)
    # 将字符串"["","","",]" 转换为列表
    res_list = [eval(i) for i in res]
    # 将二维列表转换为矩阵
    res = np.array(res_list)
    print(res)
    print(res[0])
    # 统计每一列的空元素的个数
    res_ = np.sum(res == '', axis=0)
    # print(tatal_len-res_)
    res_ls = [round(i,3) for i in (tatal_len-res_)/tatal_len]
    print(res_ls)

    return df


if __name__ == "__main__":
    read_data("正则后数据.csv")
    pass
