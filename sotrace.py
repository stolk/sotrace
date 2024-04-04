#!/bin/env python3
#
# sotrace.py
#
# shared object trace
#
# Usage:
#    sotrace.py /path/to/binary out.dot
#    dot -Tout.svg out.dot
#
# (c)2024 Bram Stolk


import os	# For popen
import sys	# For argv


# Given a target library name, see what this library directly depends on.
def dep_list(tgt) :
	cmd = "readelf -d " + tgt + " | grep NEEDED"
	f = os.popen(cmd, 'r')
	lines = f.readlines()
	f.close()
	vals = [ x.split(": ")[1].strip() for x in lines ]
	deps = [ x[1:-1] for x in vals ]
	return deps


# Given a set of dependency names, check to what path the are resolved using ldd
def dep_to_lib(tgt, deps) :
	cmd = "ldd " + tgt
	f = os.popen(cmd, 'r')
	lines = f.readlines()
	f.close()
	mapping = {}
	for line in lines:
		if "=>" in line:
			parts = line.strip().split(" => ")
			nam = parts[0].strip()
			if nam in deps :
				mapping[nam] = parts[1].split(" (")[0]
	return mapping


# Walk the dependencies of the target, and write the graph to file.
def traverse_so(tgt, nam, f, depth, visited, linked) :
	deps = dep_list(tgt)
	lib_map = dep_to_lib(tgt, deps)

	for val in lib_map.keys() :
		if nam != val and (nam,val) not in linked:
			linked.append( (nam,val) )
			f.write('"' + nam + '" -> "' + val + '"\n')

	for dep in deps:
		if dep in lib_map:
			m = lib_map[dep]
			if not m in visited:
				visited.append(m)
				dnam = os.path.basename(dep)
				traverse_so(m, dnam, f, depth+1, visited, linked)

# Main entry point
if __name__ == '__main__' :

	if len(sys.argv) != 3 :
		print("Usage:", sys.argv[0], "libfoo.so graph.dot")
		sys.exit(1)

	tgt = sys.argv[1]
	out = sys.argv[2]
	nam = os.path.basename(tgt)

	f = open(out, "w")
	f.write("digraph G {\n")
	f.write("  rankdir = LR;\n")
	traverse_so(tgt, nam, f, 0, [], [])
	f.write("}\n");
	f.close()


