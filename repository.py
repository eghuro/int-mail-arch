import logging
from git import Repo, Actor

def commit(archivedir, files):
	logger = logging.getLogger('ScanLogger')
	logger.debug("Committing changes ...")
	repo = Repo(archivedir)
	index = repo.index
	index.add(files)
	index.commit("Scanner script scanned mail")
	logger.debug("Done")
