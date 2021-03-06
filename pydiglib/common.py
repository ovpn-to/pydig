
import os, sys

PROGNAME       = os.path.basename(sys.argv[0])
PROGDESC       = "a DNS query tool written in Python"
VERSION        = "1.00"
RESOLV_CONF    = "/etc/resolv.conf"    # where to find default server
DEFAULT_PORT   = 53
ITIMEOUT       = 0.5                   # initial timeout in seconds
RETRIES        = 3                     # how many times to try
BUFSIZE        = 65535                 # socket read/write buffer size
EDNS0_UDPSIZE  = 4096
DEBUG          = False                 # for more debugging output (-d)

count_compression = 0                  # count of compression pointers derefs
size_query = 0
size_response = 0


USAGE_STRING = """\
{0} ({1}), version {2}

Usage: {0} [list of options] <qname> [<qtype>] [<qclass>]
       {0} @server +walk <zone>
Options:
        -h                        print program usage information
        @server                   server to query
        -pNN                      use port NN
        -bIP                      use IP as source IP address
        +tcp                      send query via TCP
        +aaonly                   set authoritative answer bit
        +adflag                   set authenticated data bit
        +cdflag                   set checking disabled bit
        +norecurse                set rd bit to 0 (recursion not desired)
        +edns0                    use EDNS0 with 4096 octet UDP payload
        +dnssec                   request DNSSEC RRs in response
        +hex                      print hexdump of rdata field
        +walk                     walk (enumerate) a DNSSEC secured zone
        +0x20                     randomize case of query name (bit 0x20 hack)
        -4                        perform queries using IPv4
        -6                        perform queries using IPv6
        -x                        reverse lookup of IPv4/v6 address in qname
        -d                        request additional debugging output
        -k/path/to/keyfile        use TSIG key in specified file
        -iNNN                     use specified message id
        -y<alg>:<name>:<key>      use specified TSIG alg, name, key
""".format(PROGNAME, PROGDESC, VERSION)


def dprint(input):
    if DEBUG:        print "DEBUG:", input


class ErrorMessage(Exception):
    """A friendly error message."""
    name = PROGNAME
    def __str__(self):
        val = Exception.__str__(self)
        if val:
            return '%s: %s' % (self.name, val)
        else:
            return ''


class UsageError(ErrorMessage):
    """A command-line usage error."""
    def __str__(self):
        val = ErrorMessage.__str__(self)
        if val:
            return '%s\n%s' % (val, USAGE_STRING)
        else:
            return USAGE_STRING


def excepthook(exc_type, exc_value, exc_traceback):
    """Print tracebacks for unexpected exceptions, not friendly errors."""
    if issubclass(exc_type, ErrorMessage):
        print >>sys.stderr, exc_value
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


class Counter:
    """A simple counter class"""
    def __init__(self):
        self.max = None
        self.min = None
        self.count = 0
        self.total = 0
    def addvalue(self, val):
        if self.max == None:
            self.max = val
            self.min = val
        else:
            self.max = max(self.max, val)
            self.min = min(self.min, val)
        self.count += 1
        self.total += val
    def average(self):
        return (1.0 * self.total)/self.count
