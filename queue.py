#!/usr/bin/python

import jobscheduler
import subprocess
import sys
import os
import job
import pararun
import euo
import argparse

def main():
	parser = argparse.ArgumentParser(description='Submit programm to jobscheduler')
	parser.add_argument('-q', '--queue', default=None, help='Queue config file (Default is $HOME/.queue)')
	args = parser.parse_args()

	q=jobscheduler.queue(args.queue)
	q.list()

if __name__=="__main__":
	main()
