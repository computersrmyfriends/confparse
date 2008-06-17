#!/usr/bin/env python

import optparse, sys, os
from confparse import properties

def parse_arguments():
    """Declares 2 options 'set' and 'delete', no options defaults to 'read' """

    p = optparse.OptionParser("usage: %prog [options] [initialization-file]")

    p.add_option("-s", "--set", action="store_true", default=False, help="Modify the file in place")
    p.add_option("-d", "--delete", action="store_true", default=False, help="Delete the option")

    # Parses the command line, filters the tokens in options
    # and arguments depending on what was defined previously
    o, arg = p.parse_args()

    # Basic options screening : no set and delete at the same time,
    # filename must be a file, sets must have the '=' parameter...
    
    if o.set and o.delete:
        raise Exception, "Impossible to set and delete at the same time"

    if not os.path.isfile(arg[0]):
        raise Exception, "First argument must be a file"

    if o.set:
        for a in arg[1:]:
            if a.find('=')==-1:
                raise Exception, "Options to be set must follow the format: 'opt=val'"

    return o, arg

if __name__ == '__main__':

    try:
        o, arg = parse_arguments()

        if o.set:
            d=dict( [ a.split('=') for a in arg[1:] ] )
            properties( d ).apply_to( arg[0] )

        elif o.delete:
            properties().delete( arg[1:] ).apply_to( arg[0] )

        else:
            print "\t".join( properties( arg[0] ).get( arg[1:] ) )

    except Exception,e:
        print >> sys.stderr, "Problem :", e
        sys.exit(-1)




