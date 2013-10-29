#!/bin/bash

echo "tradigist: mount agem"
ssh tradigist.th.physik.uni-bonn.de 'mount /users/stollenw/runs/agem'
echo "tradigist: mount bgem"
ssh tradigist.th.physik.uni-bonn.de 'mount /users/stollenw/runs/bgem'
echo "tradigist: mount cgem"
ssh tradigist.th.physik.uni-bonn.de 'mount /users/stollenw/runs/cgem'
echo "tradigist: mount lunz local"
ssh tradigist.th.physik.uni-bonn.de 'mount /users/stollenw/runs/lunz'

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
