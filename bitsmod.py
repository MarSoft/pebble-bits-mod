import webapp2
import sys
sys.path.append('utils')
from patcher import patch_fw

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello World!\n\n')

application = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
