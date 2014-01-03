#!/bin/bash

echo "mount agem"
sshfs stollenw@agem.th.physik.uni-bonn.de:/home/stollenw /users/stollenw/runs/agem
echo "mount bgem"
sshfs stollenw@bgem.th.physik.uni-bonn.de:/home/stollenw /users/stollenw/runs/bgem
echo "mount cgem"
sshfs stollenw@cgem.th.physik.uni-bonn.de:/home/stollenw /users/stollenw/runs/cgem
echo "mount lunz"
sshfs stollenw@lunzamsee.th.physik.uni-bonn.de:/ext/stollenw /users/stollenw/runs/lunz

ipa='131.220.161.87'
ipb='131.220.161.110'
ipc='131.220.161.65'
ipg='131.220.161.127'
ipl='131.220.162.83'
ipd='131.220.162.105'

#echo "agem: mount bgem"
#ssh agem.th.physik.uni-bonn.de "sshfs stollenw@$ipb:/home/stollenw/ /home/mnt/bgem"
#echo "agem: mount cgem"
#ssh agem.th.physik.uni-bonn.de "sshfs stollenw@$ipc:/home/stollenw/ /home/mnt/cgem"
#echo "agem: mount georg"
#ssh agem.th.physik.uni-bonn.de "sshfs stollenw@$ipg:/ext/stollenw/ /home/mnt/georg"
#echo "agem: mount deb"
#ssh agem.th.physik.uni-bonn.de "sshfs stollenw@$ipd:/ext/stollenw/ /home/mnt/deb"
