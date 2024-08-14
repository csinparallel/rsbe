# Makefile for an rsbe installation directory
# Assumes that curr working dir is named according to that installation,
# e.g., PROD_LOCAL

CWD := $(shell pwd)
INSTALLATION := $(shell basename $(CWD) | tr A-Z a-z)

all:	execpdc_$(INSTALLATION) execpdc	execpdc/execpdc.config .jobeport
	cd execpdc ; make

execpdc_$(INSTALLATION):
	git clone git@github.com:csinparallel/execpdc.git $@

execpdc:
	ln -s execpdc_$(INSTALLATION) $@

execpdc/execpdc.config:
	ln -s execpdc_$(INSTALLATION).config $@

.jobeport:
	sed -n '/^PORT=/s///p' execpdc/execpdc.config
