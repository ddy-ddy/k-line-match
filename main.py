from match_pattern.get_pattern import get_table_from_data, get_table_from_symbol, compare_table1_table2, \
    plot_kline_from_compare_info
import pandas as pd
import os
from tqdm import tqdm
import time

import logging

# 加载日志文件
format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=format, filename='data/log/info.txt')
logging.getLogger('apscheduler').setLevel(logging.WARNING)  # 设置apscheduler日记类型.
with open('data/log/info.txt', 'w') as f:
    f.write('')


class match(object):
    def __init__(self, file):
        self.file = file

    # 将所有的k线切分为多个序列，用于模式匹配。每个序列默认30根K线,默认100个序列
    def split_data(self):
        df = pd.read_csv(self.file)
        self.total_sequence = []
        data_sequence = []
        num = 3000
        for _ in tqdm(range(num), desc='切分数据'):
            for i in range(30):
                data = df.iloc[i + _, :]
                data_sequence.append(data)
            self.total_sequence.append(data_sequence)
            data_sequence = []
        print(f"数据切分完成,共切分了{num}条k线数据！")

    # 将每个序列与模式进行匹配(主要逻辑！！！)
    def batch_match(self):
        # 将数据分割
        self.split_data()
        # 用于存放找到的K线的信息
        self.data_for_plot = []

        class_get_table_from_symbol = get_table_from_symbol()
        class_get_table_from_symbol.get_description()

        # 第一个拐点之前的走势
        first_trend = class_get_table_from_symbol.first_trend
        # 拐点表2
        inflexion_table2 = class_get_table_from_symbol.inflexion_table2
        # 高低点表
        type1_table, type_1_table = class_get_table_from_symbol.type1_list, class_get_table_from_symbol.type_1_list

        # 进行匹配
        for i in tqdm(range(len(self.total_sequence)), desc='匹配中'):
            # 第一步:从真实数据中获取数据并得到序列表1和拐点表1
            class_get_table_from_data = get_table_from_data()

            # K线序列表1
            data_sequence = self.total_sequence[i]
            # 拐点表1
            class_get_table_from_data.run(data_sequence)
            inflexion_table1 = class_get_table_from_data.inflexion_table1

            # 第二步:匹配
            class_compare_table1_table2 = compare_table1_table2(data_sequence, inflexion_table1, first_trend,
                                                                inflexion_table2, type1_table, type_1_table)
            class_compare_table1_table2.compare()

            info = class_compare_table1_table2.data_for_plot

            if info != []:
                flag = True
                # 第三步：附加条件的判断(如果不想使用附加条件，则注释掉下面三行）
                flag1 = self.compare_add(data_sequence, inflexion_table1, info)
                flag2 = self.compare_add_2(data_sequence, inflexion_table1)
                flag = flag1 and flag2
                if flag:
                    self.data_for_plot.append(info)

    # 删除某个目录下的所有文件
    def del_files(self, path_file):
        ls = os.listdir(path_file)
        for i in ls:
            f_path = os.path.join(path_file, i)
            # 判断是否是一个目录,若是,则递归删除
            if os.path.isdir(f_path):
                self.del_files(f_path)
            else:
                os.remove(f_path)

    # 附加条件1的判断（判断最后一个点的数据是否低于第一个拐点,低于的话返回True)
    def compare_add(self, data_sequence, inflexion_table1, info):
        num = len(info)
        last_price = (info[num - 1]['open'] + info[num - 1]['close']) / 2
        first_inflexion_price = (data_sequence[inflexion_table1[0][0]]['open'] +
                                 data_sequence[inflexion_table1[0][0]]['close']) / 2
        if last_price <= first_inflexion_price:
            return True
        else:
            return False

    # 附加条件2的判断（幅度判断)
    def compare_add_2(self, data_sequence, inflexion_table1):
        '''
        附加条件2：
            判断第一个拐点与第二个拐点之间的幅度，大于1个点的幅度则返回True
        输入：拐点表1和对应的数据
        '''

        first_point = inflexion_table1[0][0]
        second_point = inflexion_table1[1][0]

        first_point_price = (data_sequence[first_point]['open'] + data_sequence[first_point]['close']) / 2
        second_point_price = (data_sequence[second_point]['open'] + data_sequence[second_point]['close']) / 2

        # 判断幅度
        if abs((first_point_price - second_point_price) / first_point_price) >= 0.001:
            return True
        return False

    # 运行并把所有匹配信息打印出来
    def run(self):

        self.del_files('data/save_html/')
        self.batch_match()
        class_plot_kline_from_compare_info = plot_kline_from_compare_info()
        count = 0
        for i in tqdm(range(len(self.data_for_plot)), desc='构建匹配到的K线图中'):
            count += 1
            name = f"data/save_html/匹配数据{count}.html"
            class_plot_kline_from_compare_info.run(self.data_for_plot[i], name)
        print(f"数据匹配完成！共匹配到{len(self.data_for_plot)}个K线图！图形构建完成!图形保存在data/save_html中！")
        class_plot_kline_from_compare_info.plot_total_line(self.file)


if __name__ == '__main__':
    # 使用的数据
    data_file = 'data/test_data_1.csv'

    class_name = match(data_file)
    class_name.run()
