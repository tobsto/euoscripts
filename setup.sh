#!/bin/bash

ssh heisenberg.physik.uni-bonn.de 'mount /home/stollenw/runs/agem'
ssh heisenberg.physik.uni-bonn.de 'mount /home/stollenw/runs/bgem'
ssh heisenberg.physik.uni-bonn.de 'mount /home/stollenw/runs/cgem'
ssh heisenberg.physik.uni-bonn.de 'mount /home/stollenw/runs/georg'
ssh heisenberg.physik.uni-bonn.de 'mount /home/stollenw/runs/deb'
ssh lunzamsee.th.physik.uni-bonn.de 'sshfs stollenw@stgeorgenamreith:/ext/stollenw /ext/stollenw'
