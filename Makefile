##
## Makefile
##

DIR := ${CURDIR}

doc:
	make.bat html

zip:
	python.exe ./Zipper.py