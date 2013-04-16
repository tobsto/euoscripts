#!/usr/bin/python
import argparse
import os
import subprocess
import math

parser = argparse.ArgumentParser(description='Calculate nearest neighbors in a plane of an fcc lattice')
parser.add_argument('-l', '--lattice', default='fcc', help='Lattice type')
parser.add_argument('-N', '--distance', default=2, help='Maximum distance', type=int)
parser.add_argument('-c','--coupling', help='Filename for inverse cubic coupling')
parser.add_argument('--cfile', help='Filename for c++ source code')
parser.add_argument('--flag3d', action='store_true', help='3d')
args = parser.parse_args()

# square of distance in units of a/scale. a: Lattice parameter
def distance_square_2d(scale,x,y):
	return scale*(x*x+y*y)
def distance_square_3d(scale,x,y,z):
	return scale*(x*x+y*y+z*z)

# get one corner of the lattice 
def get_lattice_fcc_plane(N):
	scale=4.0
	# fill lattice and calculate distance to origin
	lattice=[]
	for i in range(0,2*N+1):
		for j in range(0,2*N+1):
			if ((i+j)%2==0):
				x=0.5*i
				y=0.5*j
				d=distance_square_2d(scale,x,y)
				# exclude origin and points
				# outside of a circle with
				# distance N
				if (i!=0 or j!=0) and d<=scale*N*N:
					lattice.append((d, x, y))
	# sort by distance to orgin
	lattice.sort(key=lambda x: x[0])
	return scale, lattice

def get_lattice_fcc(N):
	scale=8.0
	# fill lattice and calculate distance to origin
	lattice=[]
	for i in range(0,2*N+1):
		for j in range(0,2*N+1):
			for k in range(0,2*N+1):
				if ((i+j+k)%2==0):
					x=0.5*i
					y=0.5*j
					z=0.5*k
					d=distance_square_3d(scale,x,y,z)
					# exclude origin and points
					# outside of a circle with
					# distance N
					if (not (i==0 and j==0 and k==0)) and d<=scale*N*N:
						lattice.append((d, x, y, z))
	# sort by distance to orgin
	lattice.sort(key=lambda x: x[0])
	return scale, lattice



def neighbors(lattice, flag3d):
	# all distances
	distances=[row[0] for row in lattice]
	# coordinates
	coordinates=[(row[1],row[2]) for row in lattice]
	if flag3d:
		coordinates=[(row[1],row[2],row[3]) for row in lattice]
	# all distances (without duplicates)
	reduced_distances=list(set(distances))
	reduced_distances.sort()
	
	data=[]
	count=1
	for d in reduced_distances:
		# indices of distance duplicates
		indices=[i for i, x in enumerate(distances) if x == d]
		# number of distance duplicates
		# counting 4 times and twice for coordinates which lie on an axis
		N=0
		for i in indices:
			if flag3d:
				if   coordinates[i][0]==0 and coordinates[i][1]!=0 and coordinates[i][2]!=0:
					N+=4
				elif coordinates[i][1]==0 and coordinates[i][2]!=0 and coordinates[i][0]!=0:
					N+=4
				elif coordinates[i][2]==0 and coordinates[i][0]!=0 and coordinates[i][1]!=0:
					N+=4
				elif coordinates[i][0]==0 and coordinates[i][1]==0 and coordinates[i][2]!=0:
					N+=2
				elif coordinates[i][1]==0 and coordinates[i][2]==0 and coordinates[i][0]!=0:
					N+=2
				elif coordinates[i][2]==0 and coordinates[i][0]==0 and coordinates[i][1]!=0:
					N+=2
				else:
					N+=8
			else:
				if coordinates[i][0]==0 or coordinates[i][1]==0:
					N+=2
				else:
					N+=4
	
		# corresponding coordinates
		reduced_coordinates=[coordinates[i] for i in indices]
		# remove duplicates in coordinates
		reduced_coordinates=list(set(reduced_coordinates))
		reduced_coordinates.sort()
		
		# save data
		data.append((count, d, N, reduced_coordinates))
		count=count+1
	return data

def writeCCode(outfile, data, flag3d, scale):
	f=open(outfile, 'w')
	for count, d, N, reduced_coordinates in data:
		f.write("\t\trnn[%i]=sqrt(%f/%f);\n" % (count-1, d,scale))
		f.write("\t\twnn[%i]=%i;\n" % (count-1, N))

def show(data, flag3d, scale):
	print "Order\t%i*D^2\tD\tNN\tCoordinates" % scale
	for count, d, N, reduced_coordinates in data:
		dp=math.sqrt(d/scale)
		print "%i\t%03i\t%05.2f\t%02i\t" %(count, d, dp, N), reduced_coordinates

def coupling(data, scale, output):
	f=open(output, 'w')
	j=0.0
	maxD=0
	for count, d, N, reduced_coordinates in data:
		dp=math.sqrt(d/scale)
		j+=N*1.0/pow(dp,3)
		f.write("%0.17e\t%0.17e\n" % (dp, j))
		maxD=dp
	f.close()
	print "Integrated coupling (1/x^3) at distance=%f is %0.17e" % (maxD,j)

def main():
	N=args.distance
	# get lattice
	scale=None
	lattice=None
	if (args.lattice=="fcc" and args.flag3d):
		scale, lattice = get_lattice_fcc(N)
	elif (args.lattice=="fcc" and not args.flag3d):
		scale, lattice = get_lattice_fcc_plane(N)
	else:
		print "Lattice type must be: 'fcc'. Break."
		exit(1)

	# get nearest neighbors and distances
	data=neighbors(lattice, args.flag3d)
	# print results
	show(data, args.flag3d, scale)
	# sum nearest neighbors
	if args.coupling!=None:
		coupling(data, scale, args.coupling)
	# save c++ source code
	if args.cfile!=None:
		writeCCode(args.cfile, data, args.flag3d, scale)
	
if __name__=="__main__":
	main()
