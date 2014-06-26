import webapp2
import sys,os
sys.path.append('utils')
from patcher import patch_fw

class Option(object):
    """
    This represents an option for the patch.
    """
    def __init__(self, name):
        self.name = name
        self.value = False
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
        if isinstance(self._value, bool):
            return self._value
        else:
            return self._value * self.multiplier
    @value.setter
    def value(self, value):
        if isinstance(value, bool):
            self._value = value
            return

        if isinstance(value, (int, long)) and \
                self._bounds and not self.bounds[0] <= value <= self.bounds[1]:
            raise ValueError("Value is out of bounds: %d" % value)
        self._value = value

class Patch(object):
    """
    This class represents a patch,
    with all its options.
    It can represent either "library" patch
    or be cloned to represent user-selected options state.
    """
    def __init__(self, name):
        self.name = name[:-4] # strip .php
        patchfile = open('patches/'+name)
        description = ''
        descr_done = False
        self.options = []
        self.minver = 0
        self.maxver = 65535
        for l in patchfile:
            if not descr_done and l.strip().startswith('; '):
                description += l[2:].strip() + ' '
            elif not descr_done and l.strip() == ';':
                description += '\n' # empty line to \n
            elif not descr_done and l == '\n':
                descr_done = True
                self.description = description
            elif l.startswith(';@'):
                parts = l[2:].strip().split(None, 1) # split name from value
                if not parts:
                    continue # or report?
                name=parts[0]
                opt = Option(name)
                if len(parts) > 1:
                    opt.value = parts[1]
                self.options.append(opt)
            elif l.startswith('#default'):
                parts = l.strip().split(None, 2)[1:] # cut off #default word
                if len(parts) < 2:
                    continue # illegal command? TODO: skip&report such broken file?
                name,val = parts
                if name in self.options:
                    self.options[name].value = val
            elif l.startswith('#ver'):
                parts = [int(x) for x in l.strip().split(None,2)[1:]]
                self.minver = parts[0]
                if len(parts) > 1:
                    self.maxver = parts[1]
            else:
                pass # skip all unrelated lines

patches = []
def initialize():
    """
    Runs only once.
    Reads all patches
    and constructs objects for them.
    """
    for f in os.listdir('patches'):
        if not f.endswith('.pbp'):
            continue
        patches.append(Patch(f))
initialize()

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello World!\n\n')

application = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
