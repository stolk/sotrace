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
def traverse_so(tgt, nam, f, depth, visited, linked, keep_suffix) :
	visited.add(tgt)
	deps = dep_list(tgt)
	lib_map = dep_to_lib(tgt, deps)

	for val in lib_map.keys() :
		link = (nam, val) if keep_suffix else (nam.split('.so')[0], val.split('.so')[0])
		linked.add(link)

	for dep in deps:
		if dep in lib_map:
			m = lib_map[dep]
			if not m in visited:
				visited.add(m)
				dnam = os.path.basename(dep)
				traverse_so(m, dnam, f, depth+1, visited, linked, keep_suffix)


# Walk the deps, starting from the mapped files of a process.
def trace_pid(tgt, f, visited, linked, keep_suffix) :
	nf = open("/proc/%s/comm" % (tgt,), "r")
	nam = nf.readline().strip()
	nf.close()
	cmd = "ls -l /proc/%s/map_files" % (tgt,)
	cf = os.popen(cmd, "r")
	lines = [ x.split(" -> ")[1].strip() for x in cf.readlines() if " -> " in x and ".so" in x ]
	cf.close()
	libs = sorted(set(lines))
	print("Tracing shared objects from command", nam, "with", len(lines), "mapped .so files.")
	lib_map = {}

	depth = 0

	for lib in libs:
		libname = os.path.basename(lib)
		lib_map[libname] = lib

	for val in lib_map.keys() :
		if keep_suffix :
			link = (nam, val)
			linked.add(link)
		else :
			link = (nam.split('.so')[0], val.split('.so')[0])
			linked.add(link)

	for dep in lib_map.keys() :
		if dep in lib_map :
			m = lib_map[dep]
			if not m in visited :
				visited.add(m)
				dnam = os.path.basename(dep)
				traverse_so(m, dnam, f, depth+1, visited, linked, keep_suffix)

# Main entry point
if __name__ == '__main__' :

	if len(sys.argv) != 3 :
		print("Usage:    ", sys.argv[0], "libfoo.so out.dot")
		print("Alt Usage:", sys.argv[0], "<PID> out.dot")
		sys.exit(1)

	tgt = sys.argv[1]
	out = sys.argv[2]
	nam = os.path.basename(tgt)

	f = open(out, "w")
	f.write("digraph G {\n")
	f.write("  rankdir = LR;\n")

	linked = set()
	visited = set()

	if tgt.isnumeric() :
		keep_suffix = False
		trace_pid(tgt, f, visited, linked, keep_suffix)
	else :
		keep_suffix = True
		traverse_so(tgt, nam, f, 0, visited, linked, keep_suffix)

	for link in linked :
		f.write('"' + link[0] + '" -> "' + link[1] + '"\n')

	f.write("}\n");
	f.close()


