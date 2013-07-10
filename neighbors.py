#!/usr/bin/python
import argparse
import os
import subprocess
import math

parser = argparse.ArgumentParser(description='Calculate nearest neighbors in a plane of an fcc lattice')
parser.add_argument('-l', '--lattice', default='fcc', help='Lattice type (fcc,hcp)')
parser.add_argument('-M', '--monolayer', action='store_true', help='Devide into monolayers')
parser.add_argument('-N', '--distance', default=2, help='Maximum distance', type=int)
parser.add_argument('-c','--coupling', help='Filename for inverse cubic coupling')
parser.add_argument('--cfile', help='Filename for c++ source code')
parser.add_argument('--flag3d', action='store_true', help='3d')
args = parser.parse_args()

if args.lattice!='fcc' and args.lattice!='hcp':
	parser.print_help()
	exit(1)

# square of distance in units of a/scale. a: Lattice parameter
def distance_square_2d(scale,x,y):
	return scale*(x*x+y*y)
def distance_square_3d(scale,x,y,z):
	return scale*(x*x+y*y+z*z)

#################################################
#################################################
############## FCC ##############################
#################################################
#################################################
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
	distances=[int(row[0]+0.5) for row in lattice]
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
		#print "%i\t%03i\t%05.2f\t%02i\t" %(count, d, dp, N), reduced_coordinates
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


#################################################
############## monolayer ########################
#################################################
def get_monolayers(N):
	scale=8.0
	scale_parallel=4.0
	# fill lattice and calculate distance to origin
	monolayers=[]
	for k in range(0,2*N+1):
		monolayers.append([])
		for i in range(0,2*N+1):
			for j in range(0,2*N+1):
				if ((i+j+k)%2==0):
					x=0.5*i
					y=0.5*j
					z=0.5*k
					d=distance_square_3d(scale,x,y,z)
					dpara=distance_square_2d(scale_parallel,x,y)
					# exclude origin and points
					# outside of a circle with
					# distance N
					if (not (i==0 and j==0 and k==0)) and d<=scale*N*N:
						monolayers[k].append((dpara, x, y))
		# sort by distance to orgin
		monolayers[k].sort(key=lambda x: x[0])
	return scale_parallel, scale, monolayers

def neighbors_monolayer(monolayers):
	data=[]
	for n in range(0,len(monolayers)):
		# all parallel distances
		distances=[int(row[0]+0.5) for row in monolayers[n]]
		# coordinates
		coordinates=[(row[1],row[2]) for row in monolayers[n]]
		# all distances (without duplicates)
		reduced_distances=list(set(distances))
		reduced_distances.sort()
	
		data.append([])
		count=1
		for d in reduced_distances:
			# indices of distance duplicates
			indices=[i for i, x in enumerate(distances) if x == d]
			# number of distance duplicates
			# counting 4 times and twice for coordinates which lie on an axis
			N=0
			for i in indices:
				# on the y-axis
				if   coordinates[i][0]==0 and coordinates[i][1]!=0:
					N+=2
				# on the x-axis
				elif coordinates[i][1]==0 and coordinates[i][0]!=0:
					N+=2
				# at the origin 
				elif coordinates[i][0]==0 and coordinates[i][1]==0:
					N+=1
				else:
					N+=4
	
	
			# corresponding coordinates
			reduced_coordinates=[coordinates[i] for i in indices]
			# remove duplicates in coordinates
			reduced_coordinates=list(set(reduced_coordinates))
			reduced_coordinates.sort()
			
			# save data
			data[n].append((count, d, N, reduced_coordinates))
			count=count+1
	return data

def show_monolayer(data, scale_parallel, scale):
	print "Layer\tOrder\t%i*d^2\td\tnn\t%i*D^2\tD\tCoordinates" % (scale_parallel, scale)
	for n in range(0,len(data)):
		for count, d, N, reduced_coordinates in data[n]:
			dp=math.sqrt(d/scale_parallel)
			D=distance_square_3d(scale, reduced_coordinates[0][0],reduced_coordinates[0][1],0.5*n)
			Dp=math.sqrt(D/scale)
			print "%i\t%i\t%03i\t%05.2f\t%02i\t%03i\t%05.2f\t" %(n, count, d, dp, N, D, Dp), reduced_coordinates

#################################################
#################################################
############## HCP ##############################
#################################################
#################################################
# basis vectors:	a_1= a*(1/2,  sqrt(3)/2, 0)
# 		 	a_2= a*(1/2, -sqrt(3)/2, 0)
# 		 	c_1= c*(  0,          0, 1)
#
# a,c: lattice parameter
def distance_square_hcp_2d(scale,u,v):
	return scale*(u*u+v*v-u*v)
# scale=3, cp=2.0
def distance_square_hcp_3d(scale,cp,u,v,k):
	return scale*(u*u+v*v-u*v)+cp*k*k
def coordinates_hcp_2d(u,v):
	return (u+v)*0.5, (u-v)*math.sqrt(3)/2.0 


# get one corner of the lattice 
def get_lattice_hcp_plane(Rmax):
	scale=3.0
	Npara=int(Rmax)
	# fill lattice and calculate distance to origin
	lattice=[]
	for i in range(0,Npara+1):
		for j in range(0,Npara+1):
			u=i
			v=j
			d=distance_square_hcp_2d(scale,u,v)
			# exclude origin and points
			# outside of a circle with
			# distance N
			if (i!=0 or j!=0) and d<=scale*Rmax*Rmax:
				lattice.append((d, u, v))
				print d, u, v, coordinates_hcp_2d(u,v)
	# sort by distance to orgin
	lattice.sort(key=lambda x: x[0])
	return scale,lattice

def get_lattice_hcp(Rmax):
	scale=3.0
	Npara=int(Rmax)
	c=math.sqrt(8.0/3.0)
	cp=2.0
	Nperp=int(2*Rmax/c)
	# fill lattice and calculate distance to origin
	lattice=[]
	for k in range(0,Nperp+1):
		for i in range(0,Npara+1):
			for j in range(0,Npara+1):
				u=i
				v=j
				# every second layer is shifted by 1/3 a_1 + 2/3 a_2
				if k%2!=0:
					u=u+1.0/3.0;
					v=v+2.0/3.0;
				d=distance_square_hcp_3d(scale,cp,u,v,k)
				# exclude origin and points
				# outside of a circle with
				# distance N
				if (i!=0 or j!=0 or k!=0) and d<=scale*Rmax*Rmax:
					lattice.append((d, u, v, 0.5*k))
					#print d, u, v, k, coordinates_hcp_2d(u,v), c/2*k
	# sort by distance to orgin
	lattice.sort(key=lambda x: x[0])
	return scale,lattice


def neighbors_hcp(lattice, flag3d):
	# all distances
	distances=[int(row[0]+0.5) for row in lattice]
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
		Np=0
		for i in indices:
			if flag3d:
				# in the a_2 - c plane : 3/2*2
				if   coordinates[i][0]==0 and coordinates[i][1]!=0 and coordinates[i][2]!=0:
					Np+=6
				# in the a_1 - c plane : 3/2*2
				elif coordinates[i][1]==0 and coordinates[i][2]!=0 and coordinates[i][0]!=0:
					Np+=6
				# in the a_1 - a_2 plane : 3*1
				elif coordinates[i][2]==0 and coordinates[i][0]!=0 and coordinates[i][1]!=0:
					Np+=6
				# on the c axis : 1*2
				elif coordinates[i][0]==0 and coordinates[i][1]==0 and coordinates[i][2]!=0:
					Np+=4
				# on the a_1 axis : 1.5*1
				elif coordinates[i][1]==0 and coordinates[i][2]==0 and coordinates[i][0]!=0:
					Np+=3
				# on the a_2 axis : 1.5*1
				elif coordinates[i][2]==0 and coordinates[i][0]==0 and coordinates[i][1]!=0:
					Np+=3
				else:
					Np+=12
			else:
				# on the a_1 axis or on the a_2 axis : 1.5
				if coordinates[i][0]==0 or coordinates[i][1]==0:
					Np+=3
				else:
					Np+=6
		N=Np/2
	
		# corresponding coordinates
		reduced_coordinates=[coordinates[i] for i in indices]
		# remove duplicates in coordinates
		reduced_coordinates=list(set(reduced_coordinates))
		reduced_coordinates.sort()
		
		# save data
		data.append((count, d, N, reduced_coordinates))
		count=count+1
	return data

#################################################
############## monolayer ########################
#################################################
def get_monolayers_hcp(Rmax):
	scale=3.0
	Npara=int(Rmax)
	c=math.sqrt(8.0/3.0)
	cp=2.0
	Nperp=int(2*Rmax/c)
	# fill lattice and calculate distance to origin
	monolayers=[]
	for k in range(0,Nperp+1):
		monolayers.append([])
		for i in range(0,Npara+1):
			for j in range(0,Npara+1):
				u=i
				v=j
				# every second layer is shifted by 1/3 a_1 + 2/3 a_2
				if k%2!=0:
					u=u+1.0/3.0;
					v=v+2.0/3.0;
				d=distance_square_hcp_3d(scale,cp,u,v,k)
				dpara=distance_square_hcp_2d(scale,u,v)
				# exclude origin and points
				# outside of a circle with
				# distance N
				if (i!=0 or j!=0 or k!=0) and d<=scale*Rmax*Rmax:
					monolayers[k].append((dpara, u, v))
					#print d, u, v, k, coordinates_hcp_2d(u,v), c/2*k
		# sort by distance to orgin
		monolayers[k].sort(key=lambda x: x[0])
	return scale, monolayers

def neighbors_monolayer_hcp(monolayers):
	data=[]
	for n in range(0,len(monolayers)):
		# all parallel distances
		distances=[int(row[0]+0.5) for row in monolayers[n]]
		# coordinates
		coordinates=[(row[1],row[2]) for row in monolayers[n]]
		# all distances (without duplicates)
		reduced_distances=list(set(distances))
		reduced_distances.sort()
	
		data.append([])
		count=1
		for d in reduced_distances:
			# indices of distance duplicates
			indices=[i for i, x in enumerate(distances) if x == d]
			# number of distance duplicates
			# counting 4 times and twice for coordinates which lie on an axis
			N=0.0
			for i in indices:
				# on the a_2-axis
				if   coordinates[i][0]==0 and coordinates[i][1]!=0:
					N+=1.5
				# on the a_1-axis
				elif coordinates[i][1]==0 and coordinates[i][0]!=0:
					N+=1.5
				# at the origin 
				elif coordinates[i][0]==0 and coordinates[i][1]==0:
					N+=1.0
				else:
					N+=3.0
	
	
			# corresponding coordinates
			reduced_coordinates=[coordinates[i] for i in indices]
			# remove duplicates in coordinates
			reduced_coordinates=list(set(reduced_coordinates))
			reduced_coordinates.sort()
			
			# save data
			data[n].append((count, d, N, reduced_coordinates))
			count=count+1
	return data

def show_monolayer_hcp(data, scale):
	print "Layer\tOrder\t%i*d^2\td\tnn\t%i*D^2\tD\tCoordinates" % (scale, scale)
	for n in range(0,len(data)):
		for count, d, N, reduced_coordinates in data[n]:
			dp=math.sqrt(d/scale)
			D=distance_square_hcp_3d(scale, 8.0, reduced_coordinates[0][0],reduced_coordinates[0][1],0.5*n)
			Dp=math.sqrt(D/scale)
			print "%i\t%i\t%03i\t%05.2f\t%02i\t%03i\t%05.2f\t" %(n, count, d, dp, N, D, Dp), reduced_coordinates



#################################################
#################################################
############## MAIN ROUTINE #####################
#################################################
#################################################
def main():
	N=args.distance
	if args.lattice=='fcc':
		if not (args.monolayer):
			# get lattice
			scale=None
			lattice=None
			if (args.flag3d):
				scale, lattice = get_lattice_fcc(N)
			else:
				scale, lattice = get_lattice_fcc_plane(N)
		
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
		else:	
			# get monolayer
			scale_parallel, scale, monolayers = get_monolayers(N)
			# get nearest neighbors and distances
			data=neighbors_monolayer(monolayers)
			# print results
			show_monolayer(data, scale_parallel, scale)
	else:
		if not (args.monolayer):
			# get lattice
			scale=None
			lattice=None
			#if (args.flag3d):
			#	scale, lattice = get_lattice_hcp(N)
			#else:
			if (args.flag3d):
				scale,lattice = get_lattice_hcp(N)
			else:
				scale,lattice = get_lattice_hcp_plane(N)

			# get nearest neighbors and distances
			data=neighbors_hcp(lattice, args.flag3d)
			# print results
			show(data, args.flag3d, scale)
		else:	
			# get monolayer
			scale, monolayers = get_monolayers_hcp(N)
			# get nearest neighbors and distances
			data=neighbors_monolayer_hcp(monolayers)
			# print results
			show_monolayer_hcp(data, scale)


if __name__=="__main__":
	main()
