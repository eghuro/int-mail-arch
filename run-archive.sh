#!/bin/sh

rm -rf /tmp/Maildir /tmp/international-archive
rsync -avz poseidon:~/Maildir /tmp/
git clone ssh://git@gitlab.eghuro.cz:15713/home/git/repositories/pp-cz/international-archive.git /tmp/international-archive
python archiver.py -m /tmp/Maildir -a /tmp/international-archive -l /tmp/archive.log pirati-international pirati-ppsk pirati-zo-twitter PP-EU PPI-general
