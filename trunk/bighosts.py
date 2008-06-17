

import re, os

class Address:
    '''Class with two attributes and a repr : an IPV4 or IPV6 address
    and a list of hostnames'''

    # Lazy:  every valid address matches, some incorrect address will match
    format=re.compile('(\d{1,3}\.){3}\d{1,3}')

    # Here is another that re matches ipv4 and ipv6 but I would rather ignore ipv6
    # lines since they can give up to two more names to an address:
    # localhost ::1 and fe80::1%lo0 (OSX 10.5 )
    
    # There is a free beer for the good fellow who can shed light on this 
    
    # format=re.compile(
    #         '''   (\d{1,3}\.){3}\d{1,3}				# ipv4
    #            |  ([0-9a-fA-F]{1,4}){0,7}::?([0-9a-fA-F]{1,4})	# ipv6
    #         ''',re.VERBOSE)


    def __init__(self, a, h):
        '''The address parameter is checked against the format
        regexp. self.hostnames is a list but the hostname parameter
        can be given as a list of strings or a simple string.'''

        if self.format.match(a): self.address=a
        else: raise "Address format error : %s" % a

        self.hostnames =  h


    def __repr__(self, col1width=3):
        '''Common /etc/hosts start the hostname columns at the 24th
        character and separate the two columns by as much tabs as
        needed'''

        sep="\t"*((col1width*8-1-len(self.address))/8+1)

        return repr("%s%s%s\n" % ( self.address, sep, self.hostnames ))
        

class Hosts(dict):
    '''This class features two dictionnaries addresses and hostnames
    pointing to Address instances. The dict accessors are overriden
    for the object to appear as a dictionnary which can be accessed
    both ways, depending on whether the parameter matches the address
    format'''


    # 
    #
    
    __address=Address.format

    line=re.compile(
	'''(^
		(?P<info>
                    (?P<address>	(\d{1,3}\.){3}\d{1,3})
	            (?P<sep>	\s+)
	            (?P<hostnames>	.+)    )
	        (?P<optcmt>	\s+\#.*)?
	$)|(^
		.*
	$)''', re.VERBOSE)

    def __iter__(self):
        return self

    def next(self):
        for a in self.addresses:
            yield a

    def __init__(self, defaults=None, **kwargs):
        # Ce serait sympa de creer le dict a partir d'un dict
        self.addresses={}
        self.hostnames={}
        self.filename=filename
        if filename and type(filename)==str:
            self.read(filename)
        elif filename and type(filename)==dict:
            for k,v in defaults.items(): self[k]=v
        if kwargs:
            for k,v in kwargs.items(): self[k]=v
            

    def __repr__(self):
        '''Represents itself as a common /etc/hosts file'''
        # defaults ordering anyone? localhost at the top..
        # especially useful for the ifcfg files device at the top and ipaddr right then
        lines = map( repr, self.addresses.values())
        return "".join( [ l for l in lines if l.find('~del~')==-1 ] )
                

    def __getitem__(self,item):
        '''If the item is an address, returns the hostnames, else return
        the address.'''

        if self.__address.match(item):
            return self.addresses[item].hostnames
        else:
            return self.hostnames[item].address


    def __delitem__(self,item):
        '''Removes a whole line 'address - hostnames'. Can be called
        by address or hostname'''

        if self.__address.match(item):
            a, h = item, self.addresses[item].hostnames
        else:
            a, h = self.hostnames[item].address, self.hostnames[item].hostnames

        # The references in both indexes are del. The Address
        # instance is deleted by the python garbage collector
        del self.addresses[a]
        for i in h.split(): del self.hostnames[i]
        

    def __setitem__(self, item, value):
        '''Various case : the address or host already exists. The host can be
        a list of strings. Say 10 mc'''

        if self.__address.match(item): 	a, h = item, value
        else: 				h, a = item, value

        if not a in self.addresses and ( not h in self.hostnames or h=='~del~' ):
        # New address and new hostname
        # Create an instance, and 2 references
            new=Address(a,h)
            self.addresses[a] = new 
            self.hostnames[h] = new 

        elif h in self.hostnames and not a in self.addresses:
        # Modifying the address of an existing hostname:
        # deletion of the old ref in self.addresses
        # new entry in self.addresses
        # modification of the address attribute in the instance
            del self.addresses[self[h]] 
            self.addresses[a] = self.hostnames[h]
            self.hostnames[h].address = a

        elif ( h=='~del~' or not h in self.hostnames ) and a in self.addresses:
            # Renaming an address
            # deletion of the old entries in hostnames
            # new entry in self.hostnames
            # reset of the hostnames attribute in the instance
            print self[a],h
            for i in self[a].split(' '): del self.hostnames[i] 
            self.hostnames[h] = self.addresses[a]
            self.addresses[a].hostnames = h


        elif h in self.hostnames and a in self.addresses and self[h]!=a:
        # Do we want to keep old references and alias: no
            del self[a]
            new=Address(a,h)
            self.addresses[a] = new 
            self.hostnames[h] = new 

    def reprline(self,item):
        if self.__address.match(item):
            return repr(self.addresses[item])
        else:
            return repr(self.hostnames[item])

    def append(self,item,value):
        if self.__address.match(item): 	a, h = item, value
        else: 				h, a = item, value

        self.hostnames[h]=self.addresses[a]
        self.hostnames[h].hostnames.append(h)

        
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


    def _read(self, fp):
        '''The file parameter can be a filename or a file
        descriptor. The file should conform to the common hosts format'''

        for l in fp:
            a, h = self.line.match( l).group('address', 'hostnames')
            if a:
                for i in h.split(): self[h]=a
                
    def write(self,filename=None):
        
        filename = filename or self.filename
        
        c=Hosts() # Because we pop the written lines, we pop on a copy
        c.addresses, c.hostnames = self.addresses.copy(), self.hostnames.copy()

        f=file(filename+'~','w')

        if os.path.isfile(filename):
            for l in file(filename):

                a, h = c.line.match(l).group('address', 'hostnames')

                if a:
                    for i in h.split()+[a]:
                        try: print c[i].find('~del~')
                        except: pass
                        if i in c.hostnames.keys() + c.addresses.keys() and c[i].find('~del~')!=-1:
                            f.write( self.line.sub( c.reprline(i)[:-1], l ))
                            del c[i]
                            break
                        else:
                            f.write(l)                    
                else:
                    f.write(l)

#                     else:
#                         if a in c.addresses:
#                             if c[a][0]!='~del~':
#                                 f.write( self.__address.sub( repr(c.addresses[a])[:-1], l ))
#                             del c[a]

#                         else:
#                             f.write(l)

#                if a and h:
#                     i=[ i for i in h.split(), a if i in c and c[i]!='~del~'].pop():
#                     if i:
#                         f.write( self.line.sub( repr(c.hostnames[i])[:-1], l ))
#                         del c[i]
#                     else: f.write(l)
#                else: f.write(l)
                    

        f.write(repr(c))

        f.close()
        os.rename(filename+'~',filename)
        
        

if __name__=="__main__":

    # The idea is to get the iterator to work and make write uses dict

    from os import getenv

    # Parse /etc/hosts and its different constructors (input file, kwargs and dict)

    h=Hosts()
    h['1.0.0.1']='mc'
    print h['1.0.0.1']
    print h['mc']
    del h['mc']
    print h['mc']
    
    h['mc']='1.0.0.1'
    print h['1.0.0.1']
    print h['mc']
    del h['1.0.0.1']
    print h['mc']

    h=Hosts('hosts.txt')
    h=Hosts(mc='1.0.0.1','1.0.0.2'='mc02')
    h=Hosts({'mc':'1.0.0.1','mc02':'1.0.0.2'})
    h=Hosts('/etc/hosts', {'mc':'1.0.0.1', '1.0.0.2':'mc02'})
    h=Hosts('/etc/hosts', mc03='1.0.0.3', '1.0.0.4'='mc04')
    
    # Add a name to an address, change the address of a hostname
    h.append('127.0.0.1', 'localhost.yemen')
    h.append('broadcast', '255.255.255.255')

    h['127.0.0.1']='~del~'
    h['192.0.0.1']='~del~'

    h.read()
    repr(h)
    h.write(myhost)
    print file(myhost).read()

    # Scenarios d'update de fichier hosts:


    # 1.
    h=Hosts()
    h['192.168.0.1']='mc01'
    h['mc02']='192.168.0.2'
    h['255.255.255.255']='~del~'
    h['mc02']='~del~'
    h['localhost']='10.0.0.1'
    h.append('localhost.yemen','10.0.0.1')
    h.write('hosts.txt')

    reset_testfile()
    
    # 2.
    Hosts('hosts.txt',
          localhost='1.0.0.1',
          '1.0.0.2'='mc02'
          ).write()











