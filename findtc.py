#!/usr/bin/python

# find Tc temperature sweep
def findtc(run, get_mag, run_args=(), run_first_args=(), get_mag_args=(), temperatures=None, tsteps=None, deltaM=None):

	# default magnetisation precision
	if deltaM==None:
		deltaM=1.0E-2
	# default temperatures steps
	if temperatures==None:
		temperatures=range(20,301,20)
	# default temperatures steps
	if tsteps==None:
		# default temperature increments
		tsteps=[160,80,40,20,10,5,2.5,1,0.1]
	# tsteps must contain at least one entry
	if len(tsteps)<1:
		print "Error: euorun: find_tc: No temperature steps given. Break"
		exit(1)	
	# sort tsteps
	tsteps.sort()
	# reverse order (decendent)
	tsteps.reverse()

	###############################
	# first coarse temperature scan
	###############################
	# flag determine the first run	
	first=True
	# maximal magnetisation >(3.5 + cmag)
	mag=10.0
	# limiting temperatures below and above tc
	tm=0.0
	tp=temperatures[0]
	# highest mag below tc
	mag=3.5
	mag_m=mag
	# flag determine the first run	
	first=True
	for t in temperatures: 
		# update highest temperature below Tc 
		tm=tp
		# update lowest magnetisation below tc
		mag_m=mag
		# update lowest temperature above Tc
		tp=t
		# run an add initial input for the first run
		if first:
			run(t, *run_first_args) 
		else:
			run(t, *run_args) 
		first=False
		# get magnetisation
		mag=get_mag(t, *get_mag_args)
		#print "%07.3f\t%06.4f" % (t, mag)
		# if magnetisation is below threshold abandon for loop
		if mag<=deltaM:
			break

	if mag>deltaM:
		print "Error: euorun: findtc: Did not find phase transition with the given temperatures. Break"
		exit(1)

	###############################
	# reduce list of temperatrue steps 
	# to temperature steps which are 
	# smaller than last step: tp-tm
	###############################
	if tp-tm<=tsteps[-1]:
		print "Error: euorun: find_tc: Temperature step %e is below allowed value %e. Break" % (tp-tm, tsteps[-1])
		exit(1)	
	# get list index in tsteps, where temperature steps become smaller than tp-tm
	Icut=-1
	for i in range(0,len(tsteps)-1):
		if tp-tm>tsteps[i]:
			Icut=i
			break
	tsteps=tsteps[Icut:]


	###############################
	# Automatic detailed search for Tc
	###############################
	# upper limit for temperatures (above tc)
	tmax=tp
	# increase precision (decrease temperature steps)
	for dT in tsteps:
		# start at highest known temperature below Tc 
		t=tm
		# set magnetisation below tc
		mag=mag_m
		# increase temperature until magnetisation drops below
		# deltaM or temperature above Tc is reached
		# get next temperature
		t=t+dT
		while mag>deltaM and t<tmax:
			# run an add initial input for the first run
			if first:
				run(t, *run_first_args) 
			else:
				run(t, *run_args) 
			first=False
			# get magnetisation
			mag=get_mag(t, *get_mag_args)
			if (mag>deltaM):
				# update highest temperature below Tc 
				tm=t
				# update lowest magnetisation below tc
				mag_m=mag
			# get next temperature
			t=t+dT


	# found tc
	tc=tm

	return tc


def main():
	def get_mag_dummy(t, tc, m, output):
		mag=m - m/tc * t
		if (mag<=0.0):
			mag=0.0
		f=open(output, 'a')
		f.write("%f\t%f\n" %(t, mag))
		f.close()
		return mag
		
	def run_dummy(t):
		pass

	#f=open('test_mag.dat', 'w')
	#for t in range(0,100):
	#	mag=get_mag_dummy(t, 70.0, 3.5)
	#	f.write("%f\t%f\n" % (t,mag))
	#f.close()
	
	ff=open("test_mag.dat", 'w')
	ff.close()
	tcm=(70.0, 3.5, "test_mag.dat")
	dummy=()
	findtc(run_dummy, get_mag_dummy, dummy, dummy, tcm)

if __name__=="__main__":
	main()
