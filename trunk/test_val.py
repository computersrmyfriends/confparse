import unittest, os
from test import test_support
from commands import getoutput
from tempfile import mkstemp


class ValTestCase(unittest.TestCase):
        
    def setUp(self):
        fd, self.test_file = mkstemp()
        os.write(fd, """

;; ------------- Replication and Master/Slave notification
; RmiLocalAddress=0.0.0.0
; RmiLocalPort=33099

No2xxAckReceivedTimeout=32

DEVICE=eth0:mng
IPADDR=192.168.0.1
NETMASK=192.168.0.255

ALLOW_SELF_PINGING=0  # < 0/1 > default=0
ETH_PORTS="eth0 eth1"  # < non-empty list of ethXX > default="eth0 eth1"
LOCAL_SOURCE_ADDRESS=(LOCAL_ADDRESS)  # <  > default=""
NEIGHBOURS="192.168.0.1 192.168.0.2 10.0.0.251"  # < List of IP addresses > default=""

log4j.rootLogger=ERROR
log4j.logger.com.comverse=ERROR, K
log4j.appender.K.layout.ConversionPattern=%d{dd/MM/yyyy HH:mm:ss,SSS} [%-10t] %-24c{1}\t%-5p\t%m%n

;UnknownCall.ErrorCode				= 404
; ProvNotifRequestLoad.1.max=11

[IP_Address]
remote_address=(LOCAL_ADDRESS)

path_tcap_ini=(NCXDIR)/ncxheartbeat  ; < /usr/netcentrex/ncxheartbeat > default=/usr/netcentrex/ncxheartbeat
ringBackToneUrl=file://ringin.wav

# MEM_MIN=2048
MEM_MAX=4096
SYSLOGD_OPTIONS="-m 0"

"""
            )
        os.close(fd)

    def compare_output(self, key, val):
        self.assertEqual(
            getoutput( "./val.py %s %s" % (self.test_file, key) ) ,     val )

    def set_infile(self, keysvals):
        os.system( "./val.py --set  %s %s" % (self.test_file, keysvals))

    def test_get_and_set(self):
        "Reading"

        self.compare_output(
            "log4j.logger.com.comverse log4j.appender.K.layout.ConversionPattern",
            "ERROR, K	%d{dd/MM/yyyy HH:mm:ss,SSS} [%-10t] %-24c{1}\t%-5p\t%m%n")

        self.compare_output("No2xxAckReceivedTimeout", '32' )
        self.compare_output("DEVICE", 'eth0:mng' )
        self.compare_output("ALLOW_SELF_PINGING", '0' )
        self.compare_output("ETH_PORTS" , '"eth0 eth1"')
        self.compare_output("NEIGHBOURS", '"192.168.0.1 192.168.0.2 10.0.0.251"')

    def test_update(self):
        "Updating"
        
        self.set_infile('IPADDR=10.0.0.1 NETMASK=10.0.0.255')
        self.set_infile('NEIGHBOURS="10.0.0.1"')
        self.set_infile("local_address=10.0.0.1 remote_address=10.0.0.2")
        self.set_infile('USER_MEM_ARGS="-Xms1024m -Xmx4096m"')

        self.compare_output("IPADDR	NETMASK", "10.0.0.1\t10.0.0.255")
        self.compare_output("NEIGHBOURS", "10.0.0.1")
        self.compare_output("local_address remote_address", "10.0.0.1\t10.0.0.2")
        self.compare_output('USER_MEM_ARGS', "-Xms1024m -Xmx4096m")

    def tearDown(self):
        os.remove(self.test_file)


                           
if __name__ == '__main__':
    test_support.run_unittest( ValTestCase )
