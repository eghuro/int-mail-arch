import logging
import mailbox
import email.errors
from datetime import datetime

from message import *

def scan_folder(inbox, archivedir):
        logger = logging.getLogger("ScanLogger")
	new_files = []
	for key in inbox.iterkeys():
		try:
			message = inbox[key]
		except email.errors.MessageParseError as e:
			logger.warning("Malformed message: "+e, exc_info=True)
			continue # The message is malformed. Just leave it.

		if recipient(message, "international@pirati.cz"):
			if not_spam(message):
				try:
					path = store_message(message, archivedir)
					if not path is None:
                                                logger.info(path)
						new_files.append(path)
				except TypeError as e:
					logger.exception(e)
					raise
			else:
				logger.info("SPAM: "+get_header_field(message, "Subject") + " FROM "+get_header_field(message, "From") + "[NOT STORED]")
	return new_files

def scan_maildir(maildir, archivedir, folders):
	logger = logging.getLogger('ScanLogger')
	inbox = mailbox.Maildir(maildir, factory=None)

	logger.info("Scan started")
	new_files = []
	
	logger.info("Processing inbox")
	new_files = new_files + scan_folder(inbox, archivedir)

	for folder in folders:
		logger.info("Processing "+folder)
		sub = inbox.get_folder(folder)
		new_files = new_files + scan_folder(sub, archivedir)

	logger.info("Scan finished")
	return new_files
