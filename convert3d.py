#!/usr/bin/python

#from mpl_toolkits.mplot3d import Axes3D
#from matplotlib import cm
#from matplotlib.ticker import LinearLocator, FormatStrFormatter
#import matplotlib.pyplot as plt
#import numpy as np

import argparse
import pylab

# Update database for energy shifts in EuO and substrate
def main():
	parser = argparse.ArgumentParser(description='Create 3d matrix data file from several 2d input data files')
	parser.add_argument('-i', '--input', nargs='+', help='Input 2d data file with x values in the 1st and y values in the 2nd column. Separated by tabs')
  	parser.add_argument('-o', '--output', help='Output file name')
  	parser.add_argument('-d', default=1.0, help='Distance in third direction', type=float)
  	parser.add_argument('-x', '--xpos', nargs='*', help='--positions in third direction', type=float)
  	parser.add_argument('--offset', default=0.0, help='Starting point in third direction', type=float)
  	parser.add_argument('-f', '--fourth_column', action='store_true', help='store fourth column for gnuplot use')

	args = parser.parse_args()
	
	f = open(args.output, 'w')
	for i in range(0,len(args.input)):
		data=pylab.loadtxt(args.input[i], comments='#')
		for y,z in zip(data[:,0], data[:,1]):
			if args.xpos==None:
				if args.fourth_column==False:
					f.write("%e\t%e\t%e\n" % (args.offset + i*args.d, y, z))
				else:
					f.write("%e\t%e\t%e\t%e\n" % (args.offset + i*args.d, y, z, z))
			else:
				if args.fourth_column==False:
					f.write("%e\t%e\t%e\n" % (args.xpos[i], y, z))
				else:
					f.write("%e\t%e\t%e\t%e\n" % (args.xpos[i], y, z, z))
		f.write("\n")
	f.close()

if __name__=="__main__":
	main()

#fig = plt.figure()

#ax=Axes3D(fig)

#ax = fig.gca(projection='3d')
#X = np.arange(-5, 5, 0.25)
#Y = np.arange(-5, 5, 0.25)
#X, Y = np.meshgrid(X, Y)
#R = np.sqrt(X**2 + Y**2)
#Z = np.sin(R)
#surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,
#        linewidth=0, antialiased=False)
#ax.set_zlim(-1.01, 1.01)

#ax.zaxis.set_major_locator(LinearLocator(10))
#ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

#fig.colorbar(surf, shrink=0.5, aspect=5)

#plt.show()
