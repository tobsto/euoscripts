basecmd = 'euo.out --n_cr 0.5'
output = ('-o', 'output', '/')
inputFlag=True
isoFlag=True
np=4
para_list=[]
para_list.append( ( 'n', ('d', 2), '-n', (5,) ) )
para_list.append( ( 'm', ('d', 2), '-m', (5,) ) )
para_list.append( ( 't', ('f', 5, 1), '-t', (20,40,60,70,80,90) ) )
log='interface_ni0.01_ncr0.5_n5_m5'
