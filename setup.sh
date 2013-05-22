#!/bin/bash

echo "heisenberg: mount agem"
ssh heisenberg.physik.uni-bonn.de 'mount /home/stollenw/runs/agem'
echo "heisenberg: mount bgem"
ssh heisenberg.physik.uni-bonn.de 'mount /home/stollenw/runs/bgem'
echo "heisenberg: mount cgem"
ssh heisenberg.physik.uni-bonn.de 'mount /home/stollenw/runs/cgem'
echo "heisenberg: mount georg"
ssh heisenberg.physik.uni-bonn.de 'mount /home/stollenw/runs/georg'
echo "heisenberg: mount deb"
ssh heisenberg.physik.uni-bonn.de 'mount /home/stollenw/runs/deb'
echo "lunz: mount georg"
ssh lunzamsee.th.physik.uni-bonn.de 'sshfs stollenw@stgeorgenamreith:/ext/stollenw /ext/stollenw'

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
