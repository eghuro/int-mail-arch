import os
import sys
import getopt
import logging, logging.handlers
import mailbox
import email.errors
from email.header import decode_header
from time import mktime
from email.utils import parsedate
from datetime import datetime

def lookup(message, field, addr):
	return addr in str(message[field])

def lookup_list(message, field_list, addr):
	rval = False
	for field in field_list:
		rval = rval or lookup(message, field, addr)
	return rval

def recipient(message, addr):
	field_list = ['To', 'Cc', 'Bcc', 'X-Original-To']
	return lookup_list(message, field_list, addr)

def get_header_field(message, field):
	return decode_header(message[field])[0][0]

def get_date(message):
	return datetime.fromtimestamp(mktime(parsedate(get_header_field(message, 'date'))))

def not_spam(message):
	return get_header_field(message, 'X-SPAM-Status').split(',')[0] == "No"

def store_message(message, archive_dir):
	logger = logging.getLogger('ScanLogger')
	date = get_date(message)
	
	dest = os.path.join(archive_dir, str(date.year), str(date.month), str(date.day))
	if not os.path.exists(dest):
		os.makedirs(dest)
		logger.debug("Created path: "+str(dest))
	
	subject = ''.join(e for e in get_header_field(message, 'subject') if e.isalnum())
        final_path = os.path.join(dest, subject)
        logger.debug(str(final_path))
	with open(final_path, "w") as out_file:
		out_file.write(message.as_string())

def parse_args(argv):
	m = False
	a = False

	maildir = None
	archive = None
	logfile = None

	try:
		opts, args = getopt.getopt(argv, "m:a:l:", ["maildir=", "archive=", "logfile="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-m", "--maildir"):
			m = True
			maildir = arg
		elif opt in ("-a", "--archive"):
			a = True
			archive = arg
		elif opt in ("-l", "--logfile"):
			logfile = arg

	if not (m and a): #both maildir and archive are required
		usage()
		sys.exit(2)

	return maildir, archive, logfile

def set_up_logger(logfile):
	logger = logging.getLogger('ScanLogger')
	if not logfile is None:
		logger.setLevel(logging.DEBUG)
		handler = logging.FileHandler(logfile)
		handler.setLevel(logging.DEBUG)
		logger.addHandler(handler)
	else:
		logger.disabled = True

def scan_maildir(maildir, archivedir):
	logger = logging.getLogger('ScanLogger')
	inbox = mailbox.Maildir(maildir, factory=None)

	for key in inbox.iterkeys():
	    try:
		message = inbox[key]
	    except email.errors.MessageParseError:
		continue                # The message is malformed. Just leave it.

	    if recipient(message, "international@pirati.cz"):
		if not_spam(message):
			try:
			    store_message(message, archivedir)
	    	        except TypeError as e:
		    	    logger.exception(e)
		else:
		    logger.info("SPAM: "+get_header_field(message, "Subject") + " FROM "+get_header_field(message, "From") + "[NOT STORED]")

def usage():
	print "arguments: -m|--maildir= <maildir path> -a|--archive= <where to archive> [-l|--logfile= <where to log>]"

def main(argv):
	maildir, archive, logfile = parse_args(argv)
	set_up_logger(logfile)
	scan_maildir(maildir, archive)

if __name__ == "__main__":
    main(sys.argv[1:])
