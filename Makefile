##
## Makefile
##

doc:
	make.bat html
	Move-Item -Path '.\docs\html\*' -Destination '.\docs\.' -Force
