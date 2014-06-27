import webapp2, jinja2
import sys, os, re
sys.path.append('utils')
from patcher import patch_fw

class Option(object):
    """
    This represents an option for the patch.
    """
    def __init__(self, name):
        self.name = name
        self.description = ""
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
    def is_bool(self):
        return isinstance(self.value, bool)

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
    def __init__(self, name, basename=None, patchver=None, fwver=None):
        self.name = name[:-4] # strip .php
        self.basename = basename
        self.patchver = patchver
        patchfile = open('patches/'+name)
        description = ''
        descr_done = False
        self.options = []
        option = None
        optdesc = ''
        self.minver = 0
        self.maxver = 65535
        for l in patchfile:
            if option:
                if l.startswith('; '):
                    optdesc += l[2:] # with initial spaces, if any
                    continue # to next line
                else:
                    option.description = optdesc
                    self.options.append(option)
                    option = None
                    optdesc = ''
                    # and fall to next clause to process current line
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
                default=None
                if name.startswith('+'):
                    name = name[1:]
                    default=True
                option = Option(name)
                if len(parts) > 1:
                    option.value = parts[1]
                elif default: # boolean option with default=true
                    option.value = True
                continue # try to read option description
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
    def __cmp__(self, other):
        """
        Compare by basename, then by revision,
        then reversively! by required fw version
        """
        return cmp(self.basename, other.basename) or cmp(self.patchver, other.patchver) \
            or cmp(other.minver, self.minver) # note reversed order!

patches = []
patchmap = {}
def initialize():
    """
    Runs only once.
    Reads all patches
    and constructs objects for them.
    """
    plist = os.listdir('patches')
    plist.sort()
    namereg = re.compile(r'(.*)_([0-9][0-9b][0-9])(_v([0-9]+))?')
    for f in plist:
        if not f.endswith('.pbp'):
            continue
        basename = f[:-4]
        m = namereg.match(f)
        if m:
            basename = m.group(1)
            fwver = m.group(2)
            patchver = m.group(4)
        else:
            fwver = 0
            patchver = 0
        patch = Patch(f, basename, patchver, fwver)
        patches.append(patch)
        if not basename in patchmap:
            patchmap[basename] = []
        patchmap[basename].append(patch)
    patches.sort()
initialize()

jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)+'/templates'),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True)
jinja_env.filters['nl2br'] = lambda x: x.replace('\n', '<br/>\n');

class MainPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_env.get_template('index.html')
        self.response.write(template.render({}))

class PatchesList(webapp2.RequestHandler):
    def get(self):
        ver = self.request.get('ver')
        ver = int(ver)
        mypatches = []
        mynames = []
        for patch in patches:
            if patch.basename in mynames:
                continue
            if patch.minver <= ver <= patch.maxver:
                mypatches.append(patch)
                mynames.append(patch.basename)
        template = jinja_env.get_template('patches.html')
        self.response.write(template.render({
            'patches': mypatches
        }))

class OptionsList(webapp2.RequestHandler):
    def get(self):
        patchname = self.request.get('patch')
        found = False
        for patch in patches:
            if patch.name == patchname:
                found = patch
                break
        if found:
            template = jinja_env.get_template('options.html')
            self.response.write(template.render({
                'patch': found,
                'options': found.options,
            }))
        else:
            self.response.write("Error: Patch not found")

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/patches', PatchesList),
    ('/options', OptionsList),
], debug=True)
