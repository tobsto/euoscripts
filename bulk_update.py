#!/usr/bin/python

import database
import os
import argparse

# Update database for energy shifts in EuO and substrate
def main():
	parser = argparse.ArgumentParser(description='Update database for bulk results')
	parser.add_argument('input', nargs='*', help='Folders containing results of bulk runs or folders containing subfolders with results')
  	parser.add_argument('-d', '--database', default='/home/stollenw/projects/euo/database/bulk.db', help='Database file name')
  	parser.add_argument('--overwrite', action='store_true', help='Overwrite database')
  	parser.add_argument('--no_archive', action='store_true', help='Do not archive results')
  	parser.add_argument('--archive_destination', default='/home/stollenw/projects/euo/results/bulk/', help='Archive folder')
  	parser.add_argument('--dry', action='store_true', help='Simulate updating of database')

	args = parser.parse_args()
	
	#print args.overwrite
	#print args.input
	#print args.database

	# initialize database
	t=database.bulk_database()
	# read in database if it already exists and overwrite flag is not given
	if os.path.exists(args.database) and not args.overwrite:
		t.read(args.database)
	t.fill(args.input, args.overwrite)
	if not args.dry:
		t.write(args.database)
		if not args.no_archive:
			t.archive()
	
if __name__=="__main__":
	main()
