"""
@Description: 
@Author: Ambrose
@Date: 2024-04-29 21:04:37
@LastEditTime: 2024-04-29 21:59:59
@LastEditors: Ambrose
"""

from decimal import Decimal
import pandas as pd
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Bar, Line,Page,Scatter


class Movie:
    def __init__(self):
        # 读取CSV文件
        self.data = pd.read_csv("./IMDB-Movie-Data.csv")
        self.data = self.data.fillna(0)
        
        self.bar = None
        self.line = None
        self.director_bar = {}
        self.scatter_1 = None
        self.scatter_2 = None

    # 1.统计IMDB评分各评分段的影片数。
    def count_rate_nums(self):
        # 统计评分段的影片数
        rating_counts = self.data["Rating"].value_counts().sort_index()
        rating_segments = []
        rating_counts = [0] * 9
        for i in range(1, 10):
            rating_segments.append(str(i) + "-" + str(i + 1))
            for rate in self.data["Rating"]:
                if int(rate) >= i and int(rate) < i + 1:
                    rating_counts[i - 1] += 1

        # 构建柱状图
        self.bar = (
            Bar(
                init_opts=opts.InitOpts(chart_id="bar")
            )
            .add_xaxis(rating_segments)
            .add_yaxis("电影数量", rating_counts)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="评分段电影数量统计"),
                xaxis_opts=opts.AxisOpts(name="评分段"),
                yaxis_opts=opts.AxisOpts(name="电影数量"),
            )
        )

    # 2.各年票房变化的趋势。
    def revenue_change(self):
        yearly_revenue = self.data.groupby("Year")["Revenue (Millions)"].sum()
        year = list(map(str,yearly_revenue.index))
        revenue = list(map(float,yearly_revenue.values))
        self.line = (
            Line(
                init_opts=opts.InitOpts(chart_id="line_1")
            )
            .add_xaxis(year)
            .add_yaxis(
                "票房 (百万美元)", revenue, is_smooth=True
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="年度票房统计"),
                xaxis_opts=opts.AxisOpts(name="年份"),
                yaxis_opts=opts.AxisOpts(name="票房 (百万美元)"),
            )
        )

    # 3上榜IMDB的次数最多的导演的前5位、前10位。
    def max_director(self):
        director_counts = self.data["Director"].value_counts()
        for i in [5,10]:
            top_directors = director_counts.head(i)
            top_directors_names = top_directors.index.tolist()
            top_directors_movie_counts = top_directors.values.tolist()
            line_chart_directors = (
                Line(
                    init_opts=opts.InitOpts(chart_id=f"line_{i}")
                )
                .add_xaxis(top_directors_names)
                .add_yaxis("拍摄电影数", top_directors_movie_counts, is_smooth=True, label_opts=opts.LabelOpts(is_show=True))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=f"前{i}位导演的拍摄电影数"),
                    xaxis_opts=opts.AxisOpts(name="导演名字",axislabel_opts={"rotate": 45, "interval": 0}),
                    yaxis_opts=opts.AxisOpts(name="拍摄电影数"),
                )
            )
            self.director_bar[f"{i}"] = line_chart_directors
            
    # 4.票房和Mate评分的相关性。
    def revenue_mate_relation(self):
        d = {}
        filtered_data = self.data[(self.data["Metascore"] != 0) & (self.data["Revenue (Millions)"] != 0)]
        for _,data in filtered_data.iterrows():
            key = str(data["Metascore"])
            if key in d.keys():
                d[key] += Decimal(data["Revenue (Millions)"])
            else:
                d[key] = Decimal(data["Revenue (Millions)"])
                       
        MetaScore = list(d.keys())
        Revenue = list(d.values())
        for i in range(len(MetaScore)):
            MetaScore[i] = int(eval(MetaScore[i]))
        for i in range(len(Revenue)):
            Revenue[i] = int(float(Revenue[i]))
                   
        parameter = np.polyfit(MetaScore, Revenue, 10)
        p = np.poly1d(parameter)
        
        x_data = MetaScore
        y_data = [p(data) for data in x_data]
        data_pairs = zip(x_data, y_data)
        sorted_data_pairs = sorted(data_pairs, key=lambda pair: pair[0])
        x,y = zip(*sorted_data_pairs)
                
        line = (
            Line()
            .set_global_opts(title_opts=opts.TitleOpts(title="曲线图示例"))
            .add_xaxis(x)
            .add_yaxis("拟合曲线", y,label_opts=opts.LabelOpts(is_show=False),is_smooth=True)
            .set_global_opts(
                 xaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="Meta",
                    min_=0,
                    max_=100,
                    split_number=10,  # 设置刻度数量为10
                ),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="票房",
                    min_=0,
                    max_=3000,
                    split_number=10,  # 设置刻度数量为5
                )
            )
        )
         
        self.scatter_1 = (
            Scatter(
                init_opts=opts.InitOpts(chart_id="scatter_1")
            )
            .add_xaxis(MetaScore)
            .add_yaxis("票房",Revenue,label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="Meta",
                    min_=0,
                    max_=100,
                    split_number=10,  # 设置刻度数量为10
                ),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="票房",
                    min_=0,
                    max_=3000,
                    split_number=10,  # 设置刻度数量为5
                ),
            )
        )
        self.scatter_1.overlap(line)

    # 5.时长和Mate评分的相关性
    def runtime_mate_relation(self):
        d = {}
        filtered_data = self.data[(self.data["Metascore"] != 0) & (self.data["Runtime (Minutes)"] != 0)]
        for _,data in filtered_data.iterrows():
            key = str(data["Runtime (Minutes)"])
            if key in d.keys():
                d[key] += data["Metascore"]
            else:
                d[key] = data["Metascore"]
        
        Runtime = list(d.keys())
        Metascore = list(d.values())
        for i in range(len(Runtime)):
            Runtime[i] = int(eval(Runtime[i]))
        for i in range(len(Metascore)):
            Metascore[i] = int(float(Metascore[i]))
                   
        parameter = np.polyfit(Runtime, Metascore, 3)
        p = np.poly1d(parameter)
        
        x_data = Runtime
        y_data = [p(data) for data in x_data]
        
        data_pairs = zip(x_data, y_data)
        sorted_data_pairs = sorted(data_pairs, key=lambda pair: pair[0])
        x,y = zip(*sorted_data_pairs)

        line = (
            Line()
            .set_global_opts(title_opts=opts.TitleOpts(title="曲线图示例"))
            .add_xaxis(x)
            .add_yaxis("拟合曲线", y,label_opts=opts.LabelOpts(is_show=False),is_smooth=True)
            .set_global_opts(
                 xaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="时长",
                    min_=0,
                    max_=200,
                    split_number=10,
                ),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="Meta",
                    min_=0,
                    max_=1800,
                    split_number=9,
                )
            )
        )
        self.scatter_2 = (
            Scatter(
                init_opts=opts.InitOpts(chart_id="scatter_2")
            )
            .add_xaxis(Runtime)
            .add_yaxis("Meta评分",Metascore,label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="时长",
                    min_=0,
                    max_=200,
                    split_number=10,
                ),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="Meta",
                    min_=0,
                    max_=1800,
                    split_number=9,
                ),
            )
        )
        self.scatter_2.overlap(line)

    
    def run(self):
        self.count_rate_nums()
        self.revenue_change()
        self.max_director()
        self.revenue_mate_relation()
        self.runtime_mate_relation()
        page = Page(layout=Page.DraggablePageLayout)
        bar_1 = self.director_bar["5"]
        bar_2 = self.director_bar["10"]
        page.add(
            self.bar,
            self.line,
            self.scatter_1,
            self.scatter_2,
            bar_1,
            bar_2
        )
        page.render("result.html")
        Page.save_resize_html(
            "result.html",
            cfg_file="./chart_config.json",
            dest="./result.html",
        )

if __name__ == "__main__":
    movie = Movie()
    movie.run()
    
