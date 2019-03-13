import tornado.ioloop
import tornado.web

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/08'

class Predict(tornado.web.RequestHandler):
    def initialize(self, wrapper):
        self.wrapper = wrapper

    def post(self):
        self.wrapper.run()
        self.write("Task executed successfully")

def make_app(wrapper_object):
    predict_init_args = dict(wrapper=wrapper_object)

    return tornado.web.Application([
        (r"/predict", Predict, predict_init_args),
    ])
