# sotrace
Traces the shared-object dependencies of a binary, and graphs them.

## Usage

```
./sotrace.py /path/to/foo out.dot
dot -Tsvg -o out.svg out.dot
eog out.svg
```

## Alternate Usage

It is also possible to map the actually loaded .so files of a process by giving the tool a PID instead of a file.
```
./sotrace.py PID out.dot
```

![example output](images/out-glxgears.svg "glxgears dependencies")

## Rationale

Dynamically linked binaries pull in a large amount of dependencies.
It is often hard to get a good idea of what gets pulled in, recursively.

This tool will create a graphic that clearly shows the dependencies.

It is also a useful tool to identify software bloat.

## Limitations

Currently, it will only find dependencies that are dynamically linked.

This means it will miss:
 * statically linked dependencies.

To see the dynamically loaded libraries, that were opened with `dlopen()` you need to run the tool on a PID, not a binary.

## Dependencies

To run this tool, you need python3.

To create the graph, you need dot from the graphviz package.

Personally I use eog to view the svg, but any browser would work, or also Imagemagick's display command.

## Author

Bram Stolk b.stolk@gmail.com

