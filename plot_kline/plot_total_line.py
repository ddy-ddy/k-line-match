import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Kline, Line

pd.set_option('expand_frame_repr', False)


class plot_total_line(object):
    def __init__(self):
        self.data_sequence = []
        self.data_input = []

    # 从文件中导入数据
    def get_data(self, file):
        '''
        data的数据格式为：
            open_time    2019-06-07 14:56:00
            open                     7909.96
            high                     7916.57
            low                      7906.79
            close                    7908.92
            volume                   11.8158
        '''
        self.open_time = []
        df = pd.read_csv(file)
        for i in range(len(df)):
            data = df.iloc[i, :]
            new_data = [data['open'], data['close'], data['low'], data['high']]
            open_time = str(data['open_time'])
            self.open_time.append(open_time)
            self.data_sequence.append(new_data)

    # 解析输入的数据
    def parse_input_data(self, input_data):
        '''
        data的数据格式为：
            open_time    2019-06-07 14:56:00
            open                     7909.96
            high                     7916.57
            low                      7906.79
            close                    7908.92
            volume                   11.8158
        '''
        self.data_input = []
        self.open_time = []
        for _ in range(len(input_data)):
            data = input_data[_]
            new_data = [data['open'], data['close'], data['low'], data['high']]
            open_time = str(data['open_time'])
            self.open_time.append(open_time)
            self.data_input.append(new_data)

    # 画所有数据的K线图
    def plot_k_line(self, data, file, open_time):
        '''
        data的格式：[open,close,low,high]
        '''
        _ = (

            Kline()
                .add_xaxis(["{}".format(open_time[i]) for i in range(len(data))])
                .add_yaxis("kline", data)
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(is_scale=True),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
                title_opts=opts.TitleOpts(title="K线图"),
            )
                .render(file)
        )

    def plot_k_line_2(self, data, file, open_time):
        '''
        data的格式：[open,close,low,high]
        '''
        x = []
        for i in range(len(data)):
            price = (data[i][0] + data[i][1]) / 2
            x.append(price)

        pre_data, pre_time = [], []
        last_data, last_time = [], []
        for i in range(20):
            pre_data.append([data[0][0] - 10, data[0][1] - 10, data[0][2] - 10, data[0][3] - 10])
            last_data.append([data[len(data) - 1][0] - 10, data[len(data) - 1][1] - 10, data[len(data) - 1][2] - 10,
                              data[len(data) - 1][3] - 10])
            pre_time.append(i)
            last_time.append(i)

        data = pre_data + data + last_data
        open_time = pre_time + open_time + last_time

        # kline图
        kline = (
            Kline()
                .add_xaxis(["{}".format(open_time[i]) for i in range(len(data))])
                .add_yaxis("kline", data)
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(is_scale=True),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],
                title_opts=opts.TitleOpts(title="K线图"),
            )
        )

        # line线
        line2 = (
            Line()
                .add_xaxis(["{}".format(open_time[i]) for i in range(len(data))])
                .add_yaxis(
                series_name='折线',
                y_axis=x,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False)
            )
        )

        overlap_kline_line = kline.overlap(line2)

        overlap_kline_line.render(file)

    # 运行plot_total_line，data来自文件中
    def run_data_from_file(self, file):
        self.get_data(file)
        self.plot_k_line(self.data_sequence, "data/save_html/总数据.html", self.open_time)

    # 运行plot_total_line，data来自输入的数据中
    def run_data_from_input(self, input_data, file_name):
        self.parse_input_data(input_data)
        self.plot_k_line_2(self.data_input, file_name, self.open_time)
