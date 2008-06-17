
import os, unittest

from confparse import properties, ini
from tempfile import mkstemp
from test import test_support


class propertiesFormatTestCase(unittest.TestCase):

    def setUp(self):
        self.line=properties.line

    options=(("b=c ",	('b','c',None)),
             ("c=d#e",	('c','d#e',None)),
             ("d=e;f",	('d','e;f',None)),
             ("e=f=g",	('e','f=g',None)),
             ("f=g #cmt1",	('f','g',' #cmt1')),
             ("g =h #cmt2",	('g','h',' #cmt2')),
             ("i= j #cmt3",	('i','j',' #cmt3')),
             ("j = k #cmt4",	('j','k',' #cmt4')),
             ("k=l\t #cmt5",	('k','l','\t #cmt5')), 
             ("l=m ;cmt6",	('l','m',' ;cmt6')),
             ("m=n \t ;cmt7",	('m','n',' \t ;cmt7')),
             ('n o=p',	('n o','p',None)),
             ('p=q r',	('p','q r',None)),
             (' r s = t u \t# cmt',	('r s','t u',None)),
             )

    def test_options(self):
        '''Parsing option'''
        
        for (i,(o,v,c)) in self.options:
            m=self.line.match(i)
            eq=self.assertEqual
            eq( m.group( 'option' ), o)
            eq( m.group( 'value'  ), v)
            # eq( m.group( 'optcmt' ), c)

    comments=("#cmt", " \t\t#cmt", " # \tcmt", ";cmt",
              " ; cmt"," \t\t;cmt","####cmt" )

    def test_commentsandwhitespaces(self):
        '''Parsing comments and blank lines'''

        for i in self.comments:
            self.assertEqual( self.line.match(i).group('cmted'), "cmt" )

    broken_lines=("a","a a","[a]","[a","[]","=b","a # =b",)

    def test_brokenlines(self):
        '''Broken lines'''
        for i in self.broken_lines:
            self.assertEqual( self.line.match(i), None ) 

    continuations=((" a #cmt1", 'a'),
                   (" \t [ab]\t #cmt2", '[ab]'), 
                   (" m",'m'),)
    
    def test_continuation(self):
        '''Line continuations'''
        for (i, c) in self.continuations:
            
            m=self.line.match(i)
            self.assertEqual( m.group( 'cont'  ), c)

    # What is this line,  is it an option, a comment, a continuation, or a section?
    # it is a sectption,  or maybe a continuamment!
    
    def test_ambiguous(self):
        '''Ambiguous corner case'''
        m=self.line.match
        eq=self.assertEqual
        
        eq( m("a = #b").group('option'),	 'a')
        eq( m(" l=m").group('option'),	 'l')
        eq( m("[a=b]").group('option'),	 '[a')
        eq( m("a = b = c").group('option'),	 'a')
        eq( m(" # cmt").group('cmted'),	 'cmt')
        eq( m(" # a =b").group('cmted'), 'a =b')
        eq( m(" # [a=b]").group('cmted'),'[a=b]')

class propertiesTestCase(unittest.TestCase):

    def setUp(self):
        fd,self.keyvalfile=mkstemp()
        os.write(fd, """
abc = val1  # comment
# commentaire
 abd =   le zouuuuk   ; Houu its a comment
""")
        os.close(fd)
        fd,self.emptyfile=mkstemp()
        os.close(fd)

    def tearDown(self):
        os.remove(self.keyvalfile)
        os.remove(self.emptyfile)

    def test_constructors(self):
        '''Constructors'''
        eq=self.assertEqual

        eq( properties().keys(), [] )

        i=properties( answer=42, witch='guilty' )
        eq( i['answer'], '42' )
        eq( i['witch'], 'guilty' )

        i=properties( self.keyvalfile, answer=43, witch='alwaysguilty' )
        eq( i['abc'], 'val1' )
        eq( i['answer'], '43' )
        eq( i['witch'], 'alwaysguilty' )

        i=properties( {'toto':'tata', 'titi':'toutou' }, answer=43, witch='alwaysguilty' )
        eq( i['toto'], 'tata' )
        eq( i['titi'], 'toutou' )
        eq( i['answer'], '43' )

    def test_dustbin(self):
        '''Deleting values'''
        i=properties()
        del i['tata']
        del i['toto']
        i['toto'] = '45'

        self.assertEqual( i['toto'], '45' )
        self.assertEqual( 'tata' in i.dustbin, True)
        self.assertEqual( 'toto' not in i.dustbin, True)

    def test_variables(self):
        '''Variables'''
        i=properties()
        i['tata']= 1
        i['toto']= "$tata"
        i['titi'] ="123$toto" 

        self.assertEqual( i['tata'], '1' )
        self.assertEqual( i['toto'], '$tata')
        self.assertEqual( i.get('toto'), '1')
        self.assertEqual( i.get('titi'), '1231')
    
    def test_read(self):
        '''Read'''

        i=properties()
        i.read(self.keyvalfile)
        self.assertEqual(i['abc'], 'val1')
        self.assertEqual(i['abd'], 'le zouuuuk')

    def test_write(self):
        '''Write'''
        kv=properties()
        kv['answer'], kv['witch'] = 43, 'alwaysguilty'
        kv['tata']=3
        del kv['tata']
        del kv['witch']
        kv.write(self.emptyfile)
        correct='''answer=43
'''
        self.assertEqual(file(self.emptyfile).read(),correct)
        
    def test_update(self):
        '''Update'''
        
        properties( {'abc':'bingo', 'titi':'toto'}, abd="Le hip hopppp").write(self.keyvalfile)

        correct="""
abc = bingo  # comment
# commentaire
 abd =   Le hip hopppp   ; Houu its a comment
titi=toto
"""
        self.assertEqual(file(self.keyvalfile).read(),correct)

    def addvalues(self):
        '''Adding new values to a file'''
        raise NotImplemented

    def multilines(self):
        '''Multi lines values'''
        raise NotImplemented

    def orderingvalues(self):
        '''Ordering values'''
        raise NotImplemented

    def proxy(self):
        '''Accessing items as attributes'''
        raise NotImplemented

    def test_scenario1(self):
        '''Scenario 1.'''

        properties( {'abc':'changed','titi':'toutou'}, abd="Trans go#a").write(self.keyvalfile)

        correct="""
abc = changed  # comment
# commentaire
 abd =   Trans go#a   ; Houu its a comment
titi=toutou
"""
        self.assertEqual(file(self.keyvalfile).read(),correct)

    def test_scenario2(self):
        '''Scenario 2.'''
        kv=properties( self.keyvalfile, abc="Shakira" )
        kv['tata'] = "Mul,\nti,\nPle,\nlines"
        kv['pain']='beurre'
        del kv['pain']
        del kv['abc']
        kv.write()
        
        correct="""
# commentaire
 abd =   le zouuuuk   ; Houu its a comment
tata=Mul,
	ti,
	Ple,
	lines
"""
        self.assertEqual(file(self.keyvalfile).read(),correct)


class iniFormatTestCase(unittest.TestCase):

    def setUp(self):
        self.line=ini.line

    sections=(("[a]",	'a'),
              ("[a-,_?]",	'a-,_?'),
              ('["a b"]',	'"a b"'))
    def test_sections(self):
        '''Parsing sections'''

        for (i,o) in self.sections:
            self.assertEqual( self.line.match(i).group('section'), o ) 

    options=(("b=c ",	('b','c',None)),
             ("c=d#e",	('c','d#e',None)),
             ("d=e;f",	('d','e;f',None)),
             ("e=f=g",	('e','f=g',None)),
             ("f=g #cmt1",	('f','g',' #cmt1')),
             ("g =h #cmt2",	('g','h',' #cmt2')),
             ("i= j #cmt3",	('i','j',' #cmt3')),
             ("j = k #cmt4",	('j','k',' #cmt4')),
             ("k=l\t #cmt5",	('k','l','\t #cmt5')), 
             ("l=m ;cmt6",	('l','m',' ;cmt6')),
             ("m=n \t ;cmt7",	('m','n',' \t ;cmt7')),
             ('n o=p',	('n o','p',None)),
             ('p=q r',	('p','q r',None)),
             (' r s = t u \t# cmt',	('r s','t u',None)),
             )

    def test_options(self):
        '''Parsing option'''
        
        for (i,(o,v,c)) in self.options:
            m=self.line.match(i)
            eq=self.assertEqual
            eq( m.group( 'option' ), o)
            eq( m.group( 'value'  ), v)
            # eq( m.group( 'optcmt' ), c)

    comments=("#cmt", " \t\t#cmt", " # \tcmt", ";cmt",
              " ; cmt"," \t\t;cmt","####cmt" )

    def test_commentsandwhitespaces(self):
        '''Parsing comments and blank lines'''

        for i in self.comments:
            self.assertEqual( self.line.match(i).group('cmted'), "cmt" )

    broken_lines=("a","a a","[a","[]","=b","a # =b",)

    def test_brokenlines(self):
        '''Broken lines'''
        for i in self.broken_lines:
            self.assertEqual( self.line.match(i), None ) 

    continuations=((" a #cmt1", 'a'),
                   (" \t [ab]\t #cmt2", '[ab]'), 
                   (" m",'m'),)
    
    def test_continuation(self):
        '''Line continuations'''
        for (i, c) in self.continuations:
            
            m=self.line.match(i)
            self.assertEqual( m.group( 'cont'  ), c)

    # What is this line,  is it an option, a comment, a continuation, or a section?
    # it is a sectption,  or maybe a continuamment!
    
    def test_ambiguous(self):
        '''Ambiguous corner case'''
        m=self.line.match
        eq=self.assertEqual
        
        eq( m("a = #b").group('option'),	 'a')
        eq( m(" l=m").group('option'),	 'l')
        eq( m("a = b = c").group('option'),	 'a')
        eq( m(" # cmt").group('cmted'),	 'cmt')
        eq( m(" # a =b").group('cmted'), 'a =b')
        eq( m(" # [a=b]").group('cmted'),'[a=b]')


class iniTestCase(unittest.TestCase):

    def setUp(self):
        fd,self.inifile=mkstemp()
        os.write(fd, """
[Foo Bar]
foo=bar
[Spacey Bar]
foo = bar
[Commented Bar]
foo: bar ; comment
[Long Line]
foo: this line is much, much longer than my editor
   likes it.
[Section\\with$weird%characters[\t]
[Internationalized Stuff]
foo[bg]: Bulgarian
foo=Default
foo[en]=English
foo[de]=Deutsch
[Spaces]
key with spaces : value
another with spaces = splat!
""")
        os.close(fd)
        fd,self.emptyfile=mkstemp()
        os.close(fd)

    def tearDown(self):
        os.remove(self.inifile)
        os.remove(self.emptyfile)

    def test_constructors(self):
        '''Constructors'''
        eq=self.assertEqual

        eq( ini().keys(), [] )

        i=ini( answer='42', witch='guilty' )
        i["foo"]=properties(answer='43')
        i["bar"]=properties(witch='innocent')
        eq( i['foo']['answer'], '43' )
        eq( i['bar']['witch'], 'innocent' )
        eq( i.get('foo', 'answer'), '43' )
        eq( i.get('bar', 'witch'),  'innocent')

        eq( i.get('foo', 'witch'), 'guilty' )
        eq( i.get('bar', 'answer'), '42' )
        
        i=ini( self.inifile, answer=43, witch='alwaysguilty' )
        eq( i['Foo Bar']['foo'], 'bar' )
        eq( i.get('Foo Bar','answer'), 43 )
        eq( i.get('Internationalized Stuff','witch'), 'alwaysguilty' )
        eq( i.get('Internationalized Stuff','foo'), 'Default' )

        i=ini( {'toto':'tata', 'titi':'toutou' }, answer=43, witch='alwaysguilty' )
        i['tata']=properties()
        eq( i.get('tata','toto'), 'tata' )
        eq( i.get('tata','titi'), 'toutou' )
        eq( i.get('tata','answer'), 43 )

    def test_dustbin(self):
        '''Dustbin'''
        i=ini()
        del i['tata']
        del i['toto']
        i['toto'] = '45'

        self.assertEqual( i['toto'], '45' )
        self.assertEqual( 'tata' in i.dustbin, True)
        self.assertEqual( 'toto' not in i.dustbin, True)

    def test_variables(self):
        '''Variables'''
        i=ini()
        i['section']=properties()
        i['section']['tata']= 1
        i['section']['toto']= "$tata"
        i['section']['titi'] ="123$toto" 

        self.assertEqual( i['section']['tata'], '1' )
        self.assertEqual( i['section'].get('toto'), '1')
        self.assertEqual( i['section'].get('titi'), '1231')
    
    def test_read(self):
        '''Read'''
        eq=self.assertEqual
        i=ini()
        i.read(self.inifile)
        eq( i.get('Internationalized Stuff','foo'), 'Default' )
        eq( i['Foo Bar']['foo'], 'bar' )

    def test_write(self):
        '''Write'''
        i=ini()
        i['section']=properties()
        i['section']['answer'], i['section']['witch'] = 43, 'alwaysguilty'
        i['section']['tata']=3
        del i['section']['tata']
        del i['section']['witch']
        i.write(self.emptyfile)
        correct='''[section]\nanswer=43\n
'''
        self.assertEqual(file(self.emptyfile).read(),correct)
        
    def test_update(self):
        '''Update'''
        eq=self.assertEqual
        i=ini(self.inifile)
        i['Foo Bar']['foo'] = 'bloublou'
        i['Internationalized Stuff']['witch'] = 'Burn burn !'
        i.write(self.inifile)
        i=ini(self.inifile)
        
        eq( i['Foo Bar']['foo'], 'bloublou')
        eq( i['Internationalized Stuff']['witch'], 'Burn burn !')

    def test_scenario1(self):
        '''Scenario 1.'''
        eq=self.assertEqual
        i=ini(self.inifile)
        i['Foo Bar']['foo'] = 'bloublou'
        i['Internationalized Stuff']['witch'] = 'Burn burn !'
        i.write(self.inifile)
        i=ini(self.inifile)
        
        eq( i['Foo Bar']['foo'], 'bloublou')
        eq( i['Internationalized Stuff']['witch'], 'Burn burn !')

    def scenario2(self):
        '''Scenario 2.'''
        
if __name__ == '__main__':
    test_support.run_unittest( propertiesFormatTestCase )
    test_support.run_unittest( propertiesTestCase )
    test_support.run_unittest( iniFormatTestCase )
    test_support.run_unittest( iniTestCase )




