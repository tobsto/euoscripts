#!/usr/bin/python

import subprocess
import os
import argparse
import findtc
import shutil

def get_output(N, J_4f=None, J_cf=None):
	output="mfh_N%03i" % N
	if J_4f!=None:
		output=output+"_J4f%.8f" % J_4f
	if J_cf!=None:
		output=output+"_Jcf%.8f" % J_cf
	output=output + "/"
	return output

def get_output_temp(t):
	output="t%07.3f/" % t
	return output

def run_heisenberg(t, N, output, mirror=True, longrange=False, J_4f=None, J_cf=None, cmag=None):
	output=output+get_output_temp(t)
	if not os.path.exists(output):
		os.makedirs(output)
	cmd="./heisenberg.out -t %f -n %i -o %s" % (t, N, output)
	if mirror:
		cmd=cmd+" -s"
	if longrange:
		cmd=cmd+" -l"
	if J_4f!=None:
		cmd=cmd+" --J4f %f" % J_4f
	if J_cf!=None:
		cmd=cmd+" --Jcf %f" % J_cf
	if cmag!=None:
		cmd=cmd+" --cmag %s" % cmag
	process=subprocess.Popen(cmd, shell=True)
	process.communicate()

def get_mag_heisenberg(t, output):
	magfile=output+get_output_temp(t) + "/avspin.dat"
	f=open(magfile, 'r')
	mag=float(f.readline())
	f.close()
	f=open(output + "/avspin.dat", 'a')
	f.write("%f\t%f\n" % (t, mag))	
	f.close()
	print "t=%f\tmag=%f" % (t, mag)
	return mag

def main():
	parser = argparse.ArgumentParser(description='Calculate spins and Curie temperature for the layered mean-field heisenberg model')
	parser.add_argument('-n', '--N', default=5, help='Number of layers', type=int)
	parser.add_argument('--no_mirror', action='store_false', help='Do not impose mirror symmetry')
	parser.add_argument('-l', '--longrange', action='store_true', help='Long range perpendicular coupling')
	parser.add_argument('--J4f', help='Spin-coupling', type=float)
	parser.add_argument('--Jcf', help='Spin-conduction-band-spin-coupling', type=float)
	parser.add_argument('-o','--output', help='output folder (optional)')
	args = parser.parse_args()

	output=get_output(args.N, args.J4f, args.Jcf)
	if args.output!=None:
		output=args.output + "/" + get_output(args.N, args.J4f, args.Jcf)
		
	if os.path.exists(output):
		shutil.rmtree(output)
	os.makedirs(output)
	run_args=(args.N, output, args.no_mirror, args.longrange, args.J4f, args.Jcf)
	get_mag_args=(output,)
	tc=findtc.findtc(run_heisenberg, get_mag_heisenberg, run_args, run_args, get_mag_args)
	
	f=open(output + "/tc.dat", 'w')
	f.write("%e\n" % tc)
	f.close()

	# sort avspin vs t file
	f=open(output + "/avspin.dat", 'r')
	lines=f.readlines()
	f.close()
	f=open(output + "/avspin.dat", 'w')
	data=[]
	for l in lines:
		data.append((float(l.split()[0]), float(l.split()[1])))

	data=sorted(data, key=lambda x:x[0])
	for t,mag in data:
		f.write("%f\t%f\n" % (t,mag))
	f.close()

if __name__=="__main__":
	main()
