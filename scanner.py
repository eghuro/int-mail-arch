import os
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
	#return lookup(message, 'to', addr) or lookup(message, 'cc', addr) or lookup(message, 'bcc', addr)
	# X-Original-To
	#return (addr in str(message['to'])) or (addr in str(message['cc'])) or (addr in str(message['bcc']))

def get_header_field(message, field):
	return decode_header(message[field])[0][0]

def get_date(message):
	return datetime.fromtimestamp(mktime(parsedate(get_header_field(message, 'date'))))

def store_message(message, dir):
	date = get_date(message)
	
	dest = os.path.join(dir, str(date.year), str(date.month), str(date.day))
	if not os.path.exists(dest):
		os.makedirs(dest)
		print "Created path: "+str(dest)
	
	subject = ''.join(e for e in get_header_field(message, 'subject') if e.isalnum())
        final_path = os.path.join(dest, subject)
        print str(final_path)
	with open(final_path, "w") as out_file:
		out_file.write(message.as_string())

inbox = mailbox.Maildir('/tmp/Maildir', factory=None)

for key in inbox.iterkeys():
    try:
        message = inbox[key]
    except email.errors.MessageParseError:
        continue                # The message is malformed. Just leave it.

    if recipient(message, "international@pirati.cz"):
	#print message.keys()
        if get_header_field(message, 'X-SPAM-Status').split(',')[0] == "No":
        	try:
		    store_message(message, "/home/alex/Documents/pirati/international-archive/")
		#print get_date(message)
		##print datetime.fromtimestamp(mktime(parsedate(get_header_field(message, 'date'))))
		#print get_header_field(message, 'subject')
		##print get_header_field(message, 'from')
	
		##xof = get_header_field(message, 'X-Original-From')
		##if not xof is None:
		##	print xof
		##irt = get_header_field(message, 'In-Reply-To')
		##if not irt is None:
		##	print irt
    	        except TypeError as e:
	    	    print e
        else:
            print "SPAM: "+get_header_field(message, "Subject") + " FROM "+get_header_field(message, "From")
