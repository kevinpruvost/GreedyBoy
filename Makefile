##
## Makefile
##

DIR := ${CURDIR}
SH	= powershell

doc:
	make.bat html
	$(SH) $(DIR)/docs/index.html

zip:
	python.exe ./Zipper.py