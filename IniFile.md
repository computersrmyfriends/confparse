### Apply each section to a different file ###
... work in progress

The ini object is composed of sections, every section is a properties object. Without much hassle, you can manipulate one configuration object spanning multiples files.
```
paths={'eth1':'network-scripts/ifcfg-eth1','app':'/opt/app/conf.properties'}
conf=ini()

for (name, path) in paths:
    conf.add_section(name, path)

conf.eth1.IPADDR='192.168.0.1'
conf.eth1.ONBOOT='no'
conf.app.Port='5060'

for s in conf.sections(): s.write()

```