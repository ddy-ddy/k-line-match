import pandas as pd
import os
import sys
from plot_kline.plot_total_line import plot_total_line
import logging


# 类1:从真实数据中获取数据并得到序列表1和拐点表1
class get_table_from_data(object):

    def __init__(self):
        self.data_sequence = None  # K线数据序列
        self.sequence_table1 = None  # 序列表1
        self.inflexion_table1 = None  # 拐点表1

    # 由数据得到序列表1
    def get_sequence_table1_from_data(self, data_sequence):
        '''
        序列表1：用于存放数据集中转变的序列表。
            格式：[0,1,1,-1.....]
            0为第一根K线的表示，1为涨的k线的表示，-1为跌的k线的表示，2为平的k线的表示
        '''
        self.sequence_table1 = [0]

        for i in range(1, len(data_sequence)):

            close_price_pre = data_sequence[i - 1]['close']
            close_price_now = data_sequence[i]['close']

            open_price_pre = data_sequence[i - 1]['open']
            open_price_now = data_sequence[i]['open']

            data_pre = (close_price_pre + open_price_pre) / 2
            data_now = (close_price_now + open_price_now) / 2

            # 表示此根K线相对于前一根K线是上涨的（标记为1）
            if data_now > data_pre:
                self.sequence_table1.append(1)
            # 表示此根K线相对于前一根K线是下跌的（标记为-1）
            elif data_now < data_pre:
                self.sequence_table1.append(-1)
            # 表示此根K线相对于前一根K线是不变的（标记为2）
            else:
                self.sequence_table1.append(2)

    # 根据获得的序列表1,构建拐点表1
    def get_inflexion_table1(self):
        '''
        拐点表1：用于存放拐点的数据
            格式：[[该K线在data中的位置,拐点类型]，[3,1]]
            1表示由涨转为跌的拐点，-1位由跌转为涨的拐点
        '''
        self.inflexion_table1 = []

        for i in range(len(self.sequence_table1) - 1):
            # 由涨转为跌的拐点
            if self.sequence_table1[i] == 1 and self.sequence_table1[i + 1] == -1:
                info = [i, 1]
                self.inflexion_table1.append(info)
            # 由跌转为涨的拐点
            if self.sequence_table1[i] == -1 and self.sequence_table1[i + 1] == 1:
                info = [i, -1]
                self.inflexion_table1.append(info)

    # 运行
    def run(self, data_sequence):
        self.get_sequence_table1_from_data(data_sequence)
        self.get_inflexion_table1()


# 类2:根据需要找到的K线形态表述得到拐点表2
class get_table_from_symbol(object):
    '''
    需要寻找的K线形态的表述:
        第一个拐点之前是上升还是下降？
            1 or -1
            1为上升，-1为下降
        有几个拐点？拐点类型是什么？
            构建拐点表2:[1,-1,1,-1]
            1代表由涨转跌
            -1代表由跌转涨
        相同方向的拐点的高低差是多少？
            拐点类型为1的高低差：[1,2,3,4]
            拐点类型为-1的高低差：[1,2,3,4]
    '''

    def __init__(self):
        self.first_trend = 0  # 第一个拐点之前是上升还是下降
        self.inflexion_table2 = []  # 拐点表2
        self.type1_list = []  # 拐点类型为1的高低差
        self.type_1_list = []  # 拐点类型为-1的高低差

    # 得到K线形态表述
    def get_description(self):
        print(f"请按要求输入你要识别的K线模式:")
        self.first_trend = int(input('1.请输入第一个拐点之前是上升还是下降,上升请输入1,下降请输入-1:'))
        self.inflexion_table2 = eval(input('2.请输入一个列表表示拐点个数和类型,1代表由涨转跌,-1代表由跌转涨,例如:[1,-1,1,-1]表示4个拐点:'))
        self.type1_list = eval(input("3.请输入一个列表表示拐点类型为1的高低差，例如:[1,2,3,4]表示有4个拐点类型为1的拐点，其中第四个拐点的点位最高，第一个拐点的点位最低:"))
        self.type_1_list = eval(input("4.请数一个列表表示拐点类型为-1的高低差，格式上同，例如:[2,1,3]:"))


# 类3:将拐点表1和拐点表2进行比较
class compare_table1_table2(object):
    def __init__(self, data_sequence, inflexion_table1, first_trend, inflexion_table2, type1_list, type_1_list):
        self.logger = logging.getLogger(__name__)
        self.inflexion_table1 = inflexion_table1
        self.data_sequence = data_sequence
        self.inflexion_table2 = inflexion_table2
        self.first_trend = first_trend
        self.type1_list = type1_list
        self.type_1_list = type_1_list

        # 是否匹配的标志
        self.flag_match = False

        # 匹配到的K线数据
        self.data_for_plot = []

    # 判断拐点高低差是否一致
    def compare_ratio(self, num1, num2):
        list_up, list_down = [], []
        # 首先将拐点图1按照类型分类
        for i in range(len(self.inflexion_table1)):
            type_ = self.inflexion_table1[i][1]
            if type_ == 1:
                list_up.append(self.inflexion_table1[i])
            elif type_ == -1:
                list_down.append(self.inflexion_table1[i])
            else:
                print(f"出现错误,错误发生在compare_ratio中")

        price_up, price_down = [], []  # 格式[[1,2354.1],[2,2357,8],[3,23126.9]]
        for i in range(len(list_up)):
            price = (self.data_sequence[list_up[i][0]]['open'] + self.data_sequence[list_up[i][0]]['close']) / 2
            price_up.append([i + 1, price])

        for i in range(len(list_down)):
            price = (self.data_sequence[list_down[i][0]]['open'] + self.data_sequence[list_down[i][0]]['close']) / 2
            price_down.append([i + 1, price])

        price_up = price_up[:num1]
        price_down = price_down[:num2]

        # 按照价格排序
        price_up.sort(key=lambda x: x[1])
        price_down.sort(key=lambda x: x[1])

        if self.type1_list == [x[0] for x in price_up] and self.type_1_list == [x[0] for x in price_down]:
            self.logger.info(f"匹配成功！")
            self.logger.info(
                f"匹配的K线拐点表为:{self.inflexion_table1},匹配的模式拐点表为:{self.inflexion_table2},拐点类型为1的高低差{self.type1_list},拐点类型为-1的高低差{self.type_1_list}")
            self.flag_match = True
        else:
            self.flag_match = False

    def compare(self):
        self.flag_match = False
        # 得到拐点表1的匹配数据表
        inflexion_compare = []
        for i in range(len(self.inflexion_table1)):
            info = self.inflexion_table1[i][1]
            inflexion_compare.append(info)

        # 根据拐点表2的长度进行匹配
        num = len(self.inflexion_table2)

        # 如果第一个拐点之前的走势匹配
        if self.first_trend == self.inflexion_table1[0][1]:
            # 如果拐点匹配成功（匹配条件1）
            if self.inflexion_table2 == inflexion_compare[:num]:
                self.flag_match = True
                # 如果两个拐点类型的高低差匹配成功（匹配条件2）
                self.compare_ratio(len(self.type1_list), len(self.type_1_list))
                if self.flag_match == True:
                    # 根据拐点表2和1得到数据表
                    id_end = len(self.inflexion_table2)  # 最后一个匹配到的拐点的下一个拐点的索引
                    id_data = self.inflexion_table1[id_end][0]
                    self.data_for_plot = self.data_sequence[:id_data + 1]
                else:
                    self.data_for_plot = []
            else:
                self.flag_match = False
        else:
            self.flag_match = False


# 类4：根据比较得到的信息画K线图
class plot_kline_from_compare_info(object):
    def __init__(self):
        self.plot_class1 = plot_total_line()

    # 画所有的数据的K线
    def plot_total_line(self, file):
        self.plot_class1.run_data_from_file(file)

    # 画匹配到的模式数据的K线
    def plot_match_info_line(self, data, name):
        if data == []:
            exit()
        else:
            self.plot_class1.run_data_from_input(data, name)

    def run(self, data, name):
        self.plot_match_info_line(data, name)
