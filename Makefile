# Makefile for JOBE development for RSBE, Spring 2023

# HOME = /home/rab
HOME =
# DOCKER = docker exec -t jobe
DOCKER = 

all:	rabtest.py rabtest.out new diff
#	$(DOCKER) /usr/bin/python3 /shared/rabtest.py 2>&1 | diff - $(HOME)/shared/rabtest.out
 
new new2:    rabtest.py
	$(DOCKER) /usr/bin/python3 /shared/rabtest.py 2>&1 > $(HOME)/shared/rabtest.$@

out:	rabtest.py
	$(DOCKER) /usr/bin/python3 /shared/rabtest.py > $(HOME)/shared/rabtest.out 2>&1
#	chown rab $(HOME)/shared/rabtest.out

diff:	rabtest.out rabtest.new
	diff $(HOME)/shared/rabtest.new $(HOME)/shared/rabtest.out || true

update:	rabtest.new
	cp rabtest.new rabtest.out
