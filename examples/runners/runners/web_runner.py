import json
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from surround import Runner

logging.basicConfig(level=logging.INFO)

class WebRunner(Runner):
    def prepare_runner(self):
        self.application = Application(self.assembler)

    def prepare_data(self):
        print("No data prep")

    def run(self):
        self.prepare_runner()
        self.application.listen(8080)
        logging.info("Server started at http://localhost:8080")
        tornado.ioloop.IOLoop.instance().start()


class Application(tornado.web.Application):
    def __init__(self, assembler):
        handlers = [
            (r"/message", MessageHandler, {'assembler': assembler})
        ]
        tornado.web.Application.__init__(self, handlers)


class MessageHandler(tornado.web.RequestHandler):
    def initialize(self, assembler):
        self.assembler = assembler

    def post(self):
        data = json.loads(self.request.body)

        # Clean output_data on every request
        self.assembler.surround_data.output_data = ""

        # Prepare input_date for the assembler
        self.assembler.surround_data.input_data = data["message"]

        # Execute assembler
        self.assembler.init_assembler()
        self.assembler.run()
        logging.info("Message: %s", self.assembler.surround_data.output_data)
