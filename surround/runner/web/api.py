import datetime
import tornado.ioloop
import tornado.web
import pkg_resources

# Get time for uptime calculation.
START_TIME = datetime.datetime.now()

class HealthCheck(tornado.web.RequestHandler):
    def get(self):
        self.write(dict(
            app="Surround Server",
            version=pkg_resources.get_distribution("surround").version,
            uptime=str(datetime.datetime.now() - START_TIME)
        ))

class Predict(tornado.web.RequestHandler):
    def initialize(self, wrapper):
        self.wrapper = wrapper

    def post(self):
        self.wrapper.run()
        self.write("Task executed successfully")

def make_app(wrapper_object):
    predict_init_args = dict(wrapper=wrapper_object)

    return tornado.web.Application([
        (r"/", HealthCheck),
        (r"/predict", Predict, predict_init_args),
    ])
