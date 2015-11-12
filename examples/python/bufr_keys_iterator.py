# Copyright 2005-2015 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities granted to it by
# virtue of its status as an intergovernmental organisation nor does it submit to any jurisdiction.

#
# Python implementation: bufr_keys_iterator
#
# Description: Example on how to use keys_iterator functions and the
#           codes_keys_iterator structure to get all the available
#           keys in a BUFR message.


import traceback
import sys

from eccodes import *

INPUT = '../../data/bufr/syno_1.bufr'
VERBOSE = 1  # verbose error reporting


def example():

    # open bufr file
    f = open(INPUT)

    cnt = 0

    # loop for the messages in the file
    while 1:
        # get handle for message
        gid = codes_bufr_new_from_file(f)
        if gid is None:
            break

        print "message: %s" % cnt

        # we need to instruct ecCodes to expand all the descriptors
        # i.e. unpack the data values
        # codes_set(gid,'unpack',1)

        # get key iterator for a given namespace
        iterid = codes_keys_iterator_new(gid, 'ls')

        # Different types of keys can be skipped
        # codes_skip_computed(iterid)
        # codes_skip_coded(iterid)
        # codes_skip_edition_specific(iterid)
        # codes_skip_duplicates(iterid)
        # codes_skip_read_only(iterid)
        # codes_skip_function(iterid)

        # loop over the keys
        while codes_keys_iterator_next(iterid):

            # print key name
            keyname = codes_keys_iterator_get_name(iterid)
            #keyval = codes_get_string(iterid,keyname)
            # print "%s = %s" % (keyname,keyval)
            print "  %s" % keyname

        # delete the key iterator
        codes_keys_iterator_delete(iterid)

        cnt += 1

        # delete handle
        codes_release(gid)

    # close the file
    f.close()


def main():
    try:
        example()
    except CodesInternalError, err:
        if VERBOSE:
            traceback.print_exc(file=sys.stderr)
        else:
            print >>sys.stderr, err.msg

        return 1

if __name__ == "__main__":
    sys.exit(main())
