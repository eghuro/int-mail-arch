from email.header import decode_header
from time import mktime
from email.utils import parsedate
from datetime import datetime
import logging
import os

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
        key = "X-SPAM-Status"
        if key in message:
    		head = get_header_field(message, key)
        	return head.split(',')[0] == "No"
        else:
        	return True

def store_message(message, archive_dir):
	logger = logging.getLogger('ScanLogger')
	date = get_date(message)
	
	#TODO: mesic den na dve platne cifry (01, 02, ... 10, 11) a upravit repozitar
        #TODO: dat zpravu do samostatneho adresare:
        #   - raw
        #   - hlavicky Date, From, To, Subject
        #   - text/plain (dekodovat z quoted-printable do utf-8), je-li
        #   - text/html, je-li
        #   - popr. prilohy
        dest = os.path.join(archive_dir, str(date.year), str(date.month), str(date.day))
	if not os.path.exists(dest):
		os.makedirs(dest)
		logger.debug("Created path: "+str(dest))
	
	subject = ''.join(e for e in get_header_field(message, 'subject') if e.isalnum())
	subject = subject + date.strftime("%H%M")
	final_path = os.path.join(dest, subject)
	logger.debug(str(final_path))
	if not os.path.exists(final_path):
		with open(final_path, "w") as out_file:
			out_file.write(message.as_string())
		return final_path
	else:
                # Mozna: (zapsat do tempu) a compare s puvodnim filem
		logger.debug("File exists: "+str(final_path))
		return None
