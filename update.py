#!/usr/bin/python

import euo
import argparse

# Update database for energy shifts in EuO and substrate
def main():
	parser = argparse.ArgumentParser(description='Update database for energy shifts in EuO and substrate')
	parser.add_argument('input', nargs='+', help='Folders containing results of isolated material runs')
  	parser.add_argument('-d', '--database', default='/home/stollenw/projects/euo/database/isodeltas.db', help='Database file name')
  	#parser.add_argument('-r', '--remote_database', default='stollenw@stgeorgenamreith.th.physik.uni-bonn.de:/home/stollenw/projects/euo/database/isodelta.db', help='Remote database path (e.g. user@host:/database.db)')
  	parser.add_argument('--overwrite', action='store_true', help='Overwrite database')

	args = parser.parse_args()
	
	print args.overwrite
	print args.input
	print args.database

	t=euo.isodeltabase()
	t.fill(args.input)
	
if __name__=="__main__":
	main()
