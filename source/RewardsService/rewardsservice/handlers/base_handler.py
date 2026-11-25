"""
Base handler to set header defaults for all handlers
"""
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        """
        Set the default headers to application/json for Accept and Content-Type
        """
        self.set_header('Accept', 'application/json')
        self.set_header('Content-Type', 'application/json')
