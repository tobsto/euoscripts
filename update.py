#!/usr/bin/python

import euo
import os
import argparse

# Update database for energy shifts in EuO and substrate
def main():
	parser = argparse.ArgumentParser(description='Update database for energy shifts in EuO and substrate')
	parser.add_argument('input', nargs='+', help='Folders containing results of isolated material runs')
  	parser.add_argument('-d', '--database', default='/home/stollenw/projects/euo/database/isodelta.db', help='Database file name')
  	#parser.add_argument('-r', '--remote_database', default='stollenw@heisenberg.physik.uni-bonn.de:/home/stollenw/projects/euo/database/isodelta.db', help='Remote database path (e.g. user@host:/database.db)')
  	parser.add_argument('--overwrite', action='store_true', help='Overwrite database')

	args = parser.parse_args()
	
	#print args.overwrite
	#print args.input
	#print args.database

	# initialize database
	t=euo.isodeltabase()
	# read in database if it already exists and overwrite flag is not given
	if os.path.exists(args.database) and not args.overwrite:
		t.read(args.database)
	t.fill(args.input, args.overwrite)
	t.write(args.database)
	
if __name__=="__main__":
	main()
