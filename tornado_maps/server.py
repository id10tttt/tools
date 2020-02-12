#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop
import tornado.httpserver
import logging
import time
import os
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, SymbolType


_logger = logging.getLogger(__name__)


def geo_lines() -> Geo:
    c = (
        Geo()
        .add_schema(maptype="china")
        .add(
            "",
            [("广州", 55), ("北京", 66), ("杭州", 77), ("重庆", 88)],
            type_=ChartType.EFFECT_SCATTER,
            color="white",
        )
        .add(
            "geo",
            [("广州", "上海"), ("广州", "北京"), ("广州", "杭州"), ("广州", "重庆"), ("重庆", "北京")],
            type_=ChartType.LINES,
            effect_opts=opts.EffectOpts(
                symbol=SymbolType.ARROW, symbol_size=6, color="purple"
            ),
            linestyle_opts=opts.LineStyleOpts(curve=0.2),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title="Geo-Map-Lines"))
    )

    # 返回 html
    # return c.render_embed()

    # 返回 json
    # return c.dump_options()
    # 但是无法加载

    return c.dump_options_with_quotes()


def set_default_header(self):
    # 后面的*可以换成ip地址，意为允许访问的地址
    self.set_header("Access-Control-Allow-Origin", "*")
    self.set_header("Access-Control-Allow-Headers", "x-requested-with")
    self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE")
    self.set_header("Content-Type", "application/json; charset=UTF-8")


class MapDirLine(tornado.web.RequestHandler):
    def data_received(self, chunk):
        print('chunk', chunk)
        pass

    def get(self):
        set_default_header(self)
        chart_result = geo_lines()


        # res = Geo.render(chart_result)
        print('time', time.time())
        # 返回结果
        self.write(chart_result)
        self.finish()

    def post(self, *args, **kwargs):
        print(args)


class PageHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        self.render("index.html")



def make_app():
    setting = dict(
        static_path=os.path.join(os.path.dirname(__file__), "static"),
    )

    return tornado.web.Application([
        (r"/", PageHandler),
        (r"/getMapDirLine", MapDirLine)
    ], **setting)


if __name__ == "__main__":
    port = 8889
    app = make_app()
    sockets = tornado.netutil.bind_sockets(port)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.add_sockets(sockets)
    print("Server Start Running!\nHost: {} Port: {}".format("127.0.0.1", port))
    tornado.ioloop.IOLoop.instance().start()