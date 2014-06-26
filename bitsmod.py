import webapp2
import sys
sys.path.append('utils')
from patcher import patch_fw

class Option(object):
    """
    This represents an option for the patch.
    """
    def __init__(self, name):
        self.name = name

class BoolOption(Option):
    def __init__(self, name, default=False):
        super.__init__(self,name)
        self.value = default # use setter for validation

    @property
    def value(self):
        return self._value
    @value.setter
    def setValue(self, value):
        if not isinstance(value, bool):
            raise ValueError(value)
        self._value = value

class NumericOption(Option):
    def __init__(self, name, default=0):
        super.__init__(self, name)
        self.value = default
        self._bounds = None
        self._multiplier = 1

    @property
    def bounds(self):
        return self._bounds
    @bounds.setter
    def bounds(self, lo, hi):
        if lo >= hi:
            raise ValueError("Invalid bounds: %d >= %d" % (lo,hi))
        self._bounds = (lo,hi)

    @property
    def multiplier(self):
        return self._multiplier
    @multiplier.setter
    def multiplier(self, mul):
        if mul < 1:
            raise ValueError("Illegal multiplier: %d" % mul)
        self._multiplier = mul

    @property
    def value(self):
        return self._value * self.multiplier
    @value.setter
    def value(self, value):
        if not isinstance(value, (int, long)):
            raise ValueError("Not an integer value")
        if self._bounds and not self.bounds[0] <= value <= self.bounds[1]:
            raise ValueError("Value is out of bounds: %d" % value)
        self._value = value

def initialize():
    """
    Runs only once.
    Reads all patches
    and constructs objects.
    """

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello World!\n\n')

application = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
