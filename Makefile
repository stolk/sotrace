TGT=`which glxgears`

all:
	./sotrace.py $(TGT) out.dot
	dot -Tsvg -o out.svg out.dot
	-display out.svg

