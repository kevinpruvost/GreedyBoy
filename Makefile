##
## Makefile
##

DIR := ${CURDIR}
SH	= powershell

lib:
	make -C GBDataframe/

doc:
	make.bat html
	$(SH) $(DIR)/docs/index.html

zip:
	python.exe ./Zipper.py