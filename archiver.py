import os
import sys
import time
import getopt
import logging
from repository import commit
from scanner import scan_maildir

def parse_args(argv):
	m = False
	a = False

	maildir = None
	archive = None
	logfile = None

	try:
		opts, folders = getopt.getopt(argv, "m:a:l:", ["maildir=", "archive=", "logfile="])
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

	return maildir, archive, logfile, folders

def set_up_logger(logfile, archivedir):
	formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
	logger = logging.getLogger('ScanLogger')
	if not logfile is None:
		logger.setLevel(logging.DEBUG)
		handler = logging.FileHandler(logfile)
		handler.setLevel(logging.DEBUG)
		
		handler.setFormatter(formatter)
		logger.addHandler(handler)

	logfile2 = os.path.join(archivedir, "log", time.strftime("%Y-%m-%d")+".log")
	handler2 = logging.FileHandler(logfile2)
	handler2.setLevel(logging.INFO)
	handler2.setFormatter(formatter)
	logger.addHandler(handler2)
	return logfile2

def usage():
	print "arguments: -m|--maildir= <maildir path> -a|--archive= <where to archive> [-l|--logfile= <where to log>] [folders ...]"

def main(argv):
	maildir, archive, logfile, folders = parse_args(argv)
	logfile2 = set_up_logger(logfile, archive)
	logging.getLogger('ScanLogger').debug("Script started")
	files = scan_maildir(maildir, archive, folders)
	files.append(logfile2)
	commit(archive, files)
	logging.getLogger('ScanLogger').debug("Script finished")

if __name__ == "__main__":
    main(sys.argv[1:])
