basecmd = 'euo.out -s --wru 0.01 --n_cr 0.5'
output = ('-o', '/ext/runs_version-2a001d3/interface/ni0.01_ncr0.5/output', '/')
input=None
inputFlag=True
isoFlag=True
np=49
para_list=[]
para_list.append( ( 'n', ('d', 2), '-n', (5,) ) )
para_list.append( ( 'm', ('d', 2), '-m', (5,) ) )
para_list.append( ( 'dW', ('f', 5, 3), '--Delta_W', (-0.125,) ) )
para_list.append( ( 't', ('f', 5, 1), '-t', (40,60,80,100,120,90,110,70) ) )
log='interface_ni0.01_ncr0.5_n5_m5'
