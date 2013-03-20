#!/usr/bin/python

import database
import os
import argparse

# Update database for energy shifts in EuO and substrate
def main():
	dataset_help="""Specify dataset 
	
e.g. "Metal 5 0.01" 
(for material, N and ni). 

You may use "all" as a placeholder or do not specify 
the last values e.g. "Metal all 0.01

"""

	parser = argparse.ArgumentParser(description='Update database for energy shifts in EuO and substrate')
	parser.add_argument('input', nargs='*', help='Folders containing results of isolated material runs or folders containing subfolders with results')
  	parser.add_argument('-d', '--database', default='/home/stollenw/projects/euo/database/isolated.db', help='Database file name')
	parser.add_argument('-s', '--dataset', action="store_true", help=dataset_help)
  	#parser.add_argument('-r', '--remote_database', default='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/database/isolated.db', help='Remote database path (e.g. user@host:/database.db)')
  	parser.add_argument('--overwrite', action='store_true', help='Overwrite database')
  	parser.add_argument('--archive', action='store_true', help='Archive all results')
  	parser.add_argument('--archive_destination', default='/home/stollenw/projects/euo/results/isolated/', help='Archive folder')
  	parser.add_argument('--dry', action='store_true', help='Simulate updating of database')

	args = parser.parse_args()
	
	#print args.overwrite
	#print args.input
	#print args.database

	# initialize database
	t=database.isolated_database()
	# read in database if it already exists and overwrite flag is not given
	if os.path.exists(args.database) and not args.overwrite:
		t.read(args.database)
	if not args.dataset:
		t.fill(args.input, args.overwrite)
		if not args.dry:
			t.write(args.database)
			if args.archive:
				t.archive(args.archive_destination)
			else:
				for iput in args.input:
					t.archive(args.archive_destination, None, os.path.abspath(iput))
		else:
			print "Archive folder would be: ", args.archive_destination
	else:
		t.archive(args.archive_destination, args.input)
	
if __name__=="__main__":
	main()
