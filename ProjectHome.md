The confparse python module can process simple properties files but also files with sections. It gives convenient access to the values, or gives features like variable evaluation or default values.

Configuration files can not only be read but also updated with one-liners, while keeping layout and comments intact. Options can be added, deleted, and uncommented. Confparse is extensible and can map new format without too much work.

I am circulating this alpha version to developers in the field in hopes that they can help removing the most egregious errors before too many other people see it `(*)`.


## Read a value from a file ##
Let's say your file is one of the numerous 'key=value' file such as a java properties file , a network interface file, etc.
```
from confparse import properties
http_port = properties( '/etc/my-app/config.conf' ).get( 'HttpPort' )
sip_port  = properties( '/opt/sipserver/conf.txt' ).get( 'SipPort', 5060 )
```
When you give a second argument, it is the default for the value in case the option is missing in the file.
```
host, netmask = properties( './ifcfg-eth0' ).get( ['IPADDR', 'NETMASK'] )
```
When you give a list of properties, get returns the list of corresponding values.

The properties object has an convenient attribute called 'proxy' which presents the options as attributes. It is easier to use `p.host` and `p.user` instead of `p.get( 'host' )` or `p.get( 'user' )`.
```
p = properties( "ftp.conf" ).proxy
conn = ftplib.FTP( p.host, p.user, p.password )
```



## Change a value, or delete an option ##
It is possible to change multiple options of a file at the same time. Here the IPADDR and the NETMASK address are updated:
```
properties( './ifcfg-eth0', IPADDR='192.168.0.1', NETMASK='255.255.255.0' ).write()
```

Write() has an alias called apply\_to(). Feedback from users was that the apply\_to() term would be more intuitive: the properties object can register update and suppression request which are _applied to_ an existing file.
```
properties( IPADDR='192.168.0.1', NETMASK='255.255.255.0' ).apply_to( './ifcfg-eth0' )
```
In fact, the latter is better since the file is only parsed once.

Here, the 'ONBOOT' parameter is suppressed from the file
```
properties().delete( 'ONBOOT' ).apply_to( './ifcfg-eth0' )
```

It should be stressed that comment lines, end-of-line comment, or empty lines are kept _intact_.

## From a command line ##

The val command line tool included in the package digs into configuration files to retrieve and update values for you.

  * With `val`, one can query a file over multiple options:
```
$ val ./ifcfg-eth0 IPADDR  NETMASK
192.168.0.1        255.255.255.0
```

  * ... set options :
```
$ val --set ./app.ini MEM_ARGS="-Xms1024m -Xmx4096m"
```

  * ... or delete options :
```
$ val --delete ./app.ini timeout authmode 
```

On these use cases, this script is a handy replacement of sophisticated grep, sed or awk commands. It is easier to write, and more robust since end-of-line comments and spaces are correctly trimmed out.

Stripped to the core, the script is a thin wrapper of the python module:
```
import optparse, sys, os
from confparse import properties

p = optparse.OptionParser()
p.add_option( "--set", action="store_true" )
p.add_option( "--delete", action="store_true" )
o, arg = p.parse_args()

if o.set:
    d=dict( [ a.split('=') for a in arg[1:] ] )
    properties( d ).apply_to( arg[0] )

elif o.delete:
    properties().delete( arg[1:] ).apply_to( arg[0] )

else:
    print "\t".join( properties( arg[0] ).get( arg[1:] ) )

```


## More informations ##
  * how to deal with IniFile (files with sections) or a set of files.
  * how to support NewFileFormat

See the reference documentation on :
  * the PropertiesObject
  * the IniObject

Here are suggestions on the RoadMap. Users can tell whether they find it easy to use or what feature is missing.


`(*)` this last line is neither from me nor from the Monty Python...