
import hosts, unittest
import os, sys, shutil, glob        

from test import test_support
from tempfile import mkstemp

class hostsTestCase(unittest.TestCase):

    def setUp(self):
        fd,self.hostsfile=mkstemp()
        os.write(fd, """##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
127.0.0.1	localhost localhost.yemen   # very pertinent comment
255.255.255.255	broadcasthost
::1             localhost
fe80::1%lo0	localhost
""")
        os.close(fd)
        fd,self.emptyfile=mkstemp()
        os.close(fd)

    def tearDown(self):
        os.remove(self.hostsfile)
        os.remove(self.emptyfile)

    options=(
        ("10.0.0.1\th #cmt2",	('10.0.0.1','h')),
        ("10.0.0.1\t\tj #cmt3",('10.0.0.1','j')),
        ("10.0.0.1 l\t#cmt5",	('10.0.0.1','l')), 
        ("10.0.0.1 m ;cmt6",	('10.0.0.1','m')),
        ("10.0.0.1 n \t;cmt7",	('10.0.0.1','n')),
        ("10.0.0.1 c",	('10.0.0.1','c')),
        ("10.0.0.1 d#e",	('10.0.0.1','d#e')),
        ("10.0.0.1 e;f",	('10.0.0.1','e;f')),
        ("10.0.0.1 g #cmt1",	('10.0.0.1','g')),
        )

    broken_options=(" b",
                    "\ta b",
                    " a b",
                    'p "q r"'
                    '"a b" c')

    def test_keys_values(self):
        '''Parsing regexp'''
        line=Hosts().line
        for (i,(a,h)) in self.options:
            m=line.match(i)
            self.assertEqual( m.group('address'),   a ) 
            self.assertEqual( m.group('hostnames'), h )


        for i in self.broken_options:
            self.assertEqual( line.match(i), None )


    def test_set_get(self):
        '''Set and get'''
        h=Hosts()

        h['10.0.0.1']='mc'
        h['mc']='10.0.0.1'
        h['10.0.0.2']='mc01'
        h['mc01']='10.0.0.3'

        self.assertEqual(h['10.0.0.3'],	'mc01')
        self.assertEqual(h['10.0.0.1'],	'mc')
        self.assertEqual(h['mc01'],	'10.0.0.3')
        self.assertEqual(h['mc'],	'10.0.0.1')
        self.assertRaises(Exception,h.__setitem__,'hostname','hostname')
        self.assertRaises(Exception,h.__setitem__,'10.0.0.0','10.0.0.0')
        # h['address']='address'

        
    def test_del(self):
        '''Del'''
        h=Hosts()

        h['mc'], h['mc02'], h['127.0.0.1'] = '10.0.0.1', '10.0.0.2', 'localhost'
        del h['10.0.0.1']
        del h['mc02']
        del h['localhost']
        self.assertRaises(KeyError, h.__delitem__, 'tata')
        self.assertEqual(h.keys(), [])

    def test_append(self):
        '''Append'''
        eq=self.assertEqual
        h=Hosts()

        h['mc']='10.0.0.1'
        h.append('10.0.0.1','localhost')
        eq(h['10.0.0.1'],'mc localhost')

        h.append('localhost', 'localhost.yemen')
        eq(h['10.0.0.1'],'mc localhost localhost.yemen')

        h.append('localhost', 'mc')
        eq(h['10.0.0.1'],'mc localhost localhost.yemen')

        self.assertRaises(KeyError, h.append, 'tata', '192.168.0.1')

    def test_read(self):
        '''Read'''
        eq=self.assertEqual
        h=Hosts()
        h.read(self.hostsfile)

        eq(h.keys(), ['localhost.yemen', 'broadcasthost', 'localhost', '127.0.0.1', '255.255.255.255'])
        eq(h['broadcasthost'],'255.255.255.255')
        eq(h['127.0.0.1'],'localhost localhost.yemen')
        eq(h['localhost.yemen'],'127.0.0.1')
        eq(h['localhost'],'127.0.0.1')

    
    def test_constructor(self):
        '''Constructors and read'''
        eq=self.assertEqual
        h=Hosts()
        eq(h.keys(),[])
                      
        h=Hosts(mc='1.0.0.1', mc02='1.0.0.2')
        eq(h['mc'],'1.0.0.1')
        eq(h['mc02'],'1.0.0.2')
        eq(h['1.0.0.1'],'mc')
        eq(h['1.0.0.2'],'mc02')

        h=Hosts({'pc':'1.0.0.3','pc02':'1.0.0.4'})
        eq(h['pc'],'1.0.0.3')
        eq(h['pc02'],'1.0.0.4')
        eq(h['1.0.0.3'],'pc')
        eq(h['1.0.0.4'],'pc02')
        
        h=Hosts(self.hostsfile, ac03='1.0.0.5', ac02='1.0.0.6')
        eq(h['ac03'],'1.0.0.5')
        eq(h['ac02'],'1.0.0.6')
        eq(h['broadcasthost'],'255.255.255.255')
        eq(h['127.0.0.1'],'localhost localhost.yemen')
        eq(h['localhost.yemen'],'127.0.0.1')
        eq(h['localhost'],'127.0.0.1')

    def test_write(self):
        '''Write'''

        h=Hosts()
        h['localhost'], h['mc02'] = '1.0.0.1', '1.0.0.2'
        h.write(self.emptyfile)
        h.write(self.emptyfile)

        correct = '1.0.0.1\t\t\tlocalhost\n1.0.0.2\t\t\tmc02\n'
        self.assertEqual(file(self.emptyfile).read(), correct)

    def test_update(self):
        '''Update'''
        h=Hosts(self.hostsfile, mc02='1.0.0.2', localhost='10.0.0.2')
        h.write()

        correct =  """##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
10.0.0.2		localhost localhost.yemen   # very pertinent comment
255.255.255.255		broadcasthost
::1             localhost
fe80::1%lo0	localhost
1.0.0.2			mc02
"""
        self.assertEqual(file(self.hostsfile).read(), correct)
    
    def test_scenario1(self):
        '''Scenario 1.'''

        Hosts(self.hostsfile, localhost='1.0.0.1',mc02='1.0.0.2').write()

        correct =  """##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
1.0.0.1		localhost localhost.yemen   # very pertinent comment
255.255.255.255		broadcasthost
::1             localhost
fe80::1%lo0	localhost
1.0.0.2			mc02
"""
        self.assertEqual(file(self.hostsfile).read(), correct)

    def test_scenario2(self):
        '''Scenario 2.'''
        d=dict([ ('localhost','1.0.0.1'), ('1.0.0.2','mc02') ])
        Hosts(d).write(self.emptyfile)

        correct = '1.0.0.1\t\t\tlocalhost\n1.0.0.2\t\t\tmc02\n'
        self.assertEqual(file(self.emptyfile).read(), correct)


    def test_scenario3(self):
        '''Scenario 3.'''
        h=Hosts(self.hostsfile)
        h['localhost'] =  '10.0.0.3'
        h['10.0.0.3'] ='toto'
        del h['toto']
        del h['broadcasthost']
        
        # Add a name to an address, change the address of a hostname
        h['localhost'] =  '127.0.0.1'
        h.append('localhost', 'localhost.yemen')

        del h['127.0.0.1']
        h.write(self.emptyfile)
        
        correct =  """##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
1.0.0.1		localhost localhost.yemen   # very pertinent comment
::1             localhost
fe80::1%lo0	localhost
1.0.0.2			mc02
"""


        self.assertEqual(file(self.emptyfile).read(), '')


if __name__ == '__main__':

    from hosts import Hosts
    test_support.run_unittest(hostsTestCase)

#     from hosts import Hosts TODO
#     test_support.run_unittest(iniformatTestCase)

