
import re, os

class Hosts(dict):
    # do not expect update, items, keys, and values to work correctly
    # on this weird dikshunnary

    
    address=re.compile('(\d{1,3}\.){3}\d{1,3}')

    def __init__(self, defaults=None, **kwargs):
        self.dustbin = []
        
        if type(defaults)==str:
            self.filename=defaults
            self.read(defaults)

        elif hasattr(defaults,'__setitem__'):
            if hasattr(defaults, 'dustbin'):
                self.dustbin = defaults.dustbin
            for a,h in defaults.items():
                 h=h.split()
                 self[a]=h.pop(0)
                 for i in h: self.append(a,i)

        if kwargs:
            for a,h in kwargs.items():
                h=h.split()
                self[a]=h.pop(0)
                for i in h: self.append(a,i)

    # update and items should be overidden

    # Shortcut to the dict set and del methods (Hosts do no override get)
    def dset(self,item, value): dict.__setitem__(self, item, value)
    def ddel(self,item): 	dict.__delitem__(self, item)            

    def __setitem__(self, item, value):
        if self.address.match(item) and not self.address.match(value):
            a, h = item, value
        elif self.address.match(value) and not self.address.match(item):
            a, h = value, item
        else:
            raise Exception,"Error item '%s' or value '%s' must be an address " % (item,value)

        # The address argument already exists
        if a in self:
            # Suppress every old hostname entries poing to a
            for i in self[a].split(): self.ddel( i)

            self.dset( a, h)
            self.dset( h, a)

        # The hostname argument already exists ( the address
        # argument is unkown)
        elif h in self:
            olda = self[h]
            h = self[olda]

            # Creating the new address entry
            self.dset(a, h)

           # updating the entries pointing to the old address
            for i in h.split(): self.dset(i,a)

            # Suppress the old address entries poing to a
            self.ddel( olda)
 
        # The relation address -- hostname is new
        else:
            self.dset(a, h)
            self.dset(h, a)

        for i in a,h:
            if i in self.dustbin: self.dustbin.remove(i)
    

    def __delitem__(self,item):
        
        if self.address.match(item):
            a, h = item, self[item]
        else:
            a, h = self[item], self[self[item]]

        for i in h.split() + [a]: self.ddel(i)
        for i in a,h: self.dustbin.append(i)


    def __repr__(self):
        lines=[ "%s%s%s" % (a, "\t"*self.align(a), self[a]) for a in self.addresses() ]
        if lines:
            return "\n".join(lines)+'\n'
        else: return ''

    def align(self,a):
        return ((23-len(a))/8+1)

    def addresses(self):
        a = [ a for a in self if self.address.match(a) ]
        
        if '127.0.0.1' in sorted(a) :
            a.remove('127.0.0.1')
            a.insert(0, '127.0.0.1')
        return a        
    
    def reprline(self,item):
        if self.address.match(item):
            a, h = item, self[item]
        else:
            a, h = self[item], self[self[item]]

        return "%s%s%s" % (a, "\t"*((23-len(item))/8+1), h)

    def append(self,item,value):
        if self.address.match(item):
            a, h = item, value
        elif self.address.match(value):
            a, h = value, item
        else:
            a, h = self[item], value

        if self[a].find(h)!=-1: return

        self.dset(a,  "%s %s" % (self[a], h ))
        self.dset(h, a)

    def read(self,filenames):
        """Read and parse a filename or a list of filenames.

        Files that cannot be opened are silently ignored; this is
        designed so that you can specify a list of potential
        configuration file locations (e.g. current directory, user's
        home directory, systemwide directory), and all existing
        configuration files in the list will be read.  A single
        filename may also be given.

        Return list of successfully read files.
        """

        if isinstance(filenames, basestring):
            filenames = [filenames]
        read_ok = []
        for filename in filenames:
            try:
                fp = open(filename)
            except IOError:
                continue
            self._read(fp)
            fp.close()
            read_ok.append(filename)
        return read_ok 

    line=re.compile(
	'''(^
           	(?P<address>	(\d{1,3}\.){3}\d{1,3})
	        (?P<sep>	\s+)
	        (?P<hostnames>	(((?!\s+(\#|;)).)|\S)*)
	)''', re.VERBOSE)

    def _read(self, fp):
        '''The file parameter can be a filename or a file
        descriptor. The file should conform to the common hosts format'''

        for l in fp:
            m = self.line.match( l )
            if not m: continue
            a, h = m.group('address', 'hostnames')
            if a: 
                h=h.split()
                self[a]=h.pop(0)
                for i in h: self.append(a,i)
                
    def write(self, filename=None, order=None):
        
        filename = filename or self.filename
        # if we can write in an open file then we can write on stdout TODO...

        # Because we pop the written lines, we need to pop on a _copy_
        # Self must be filtered out from hostnames keys so that multi
        # hostnames are properly handled.

        c=Hosts( dict([ i for i in self.items() if self.address.match( i[0] ) ]) )
        f=file(filename+'~','w')

        if os.path.isfile(filename):
            for l in file(filename):
                m = c.line.match( l )
                if not m:
                    f.write(l)
                    continue
                
                a, h = m.group('address', 'hostnames')

                if a:
                    # pops an address or hostname for the confile
                    # which is configured and which is not set for suppresion
                    i=[ i for i in h.split()+ [a] if i in c ] 
                    if i:
                        i=i.pop()
                        if i not in c.dustbin:
                            f.write( self.line.sub( self.reprline(i), l ))
                        else : pass
                        del c[i]
                    else: f.write(l)
                else: f.write(l)

        f.write(repr(c))

        f.close()
        os.rename(filename+'~',filename)

if __name__=='__main__':
    # une nouvelle relation
    # un hostname qui change de nom
    # un fqdn qui change d'addresse
    # une suppression de relation
    # le setitem ecrase les hostnames existant si l'adresse
    # existe. Si le hostname existe et l'adresse est neuve:
    # les hostnames sont balayes

    # Ordering ...

    print Hosts.line.match('1.0.0.1                  localhost    # very').groups()[0]
    print Hosts.line.sub('127.0.0.1\t\tlocalhost','1.0.0.1                  localhost    # very')
    h=Hosts()

    h['mc']='10.0.0.1'
    h['mc02']='10.0.0.2'
    h.append('10.0.0.1','localhost')
    print h.addresses()
    print "2 lines, localhost is aliased\n", h

    h['localhost'] =  '10.0.0.3'
    print "2 lines, localhost's addr is changed\n", h

    h['10.0.0.3'] ='toto'    
    print "2 lines, localhost renamed toto\n", h

    del h['toto']
    del h['10.0.0.2']
    print "2 lines deleted, nothin' left\n", h


    
