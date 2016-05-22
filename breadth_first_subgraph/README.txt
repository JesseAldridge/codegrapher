
# Generate the full callgraph
codegrapher -r . --output ~/Desktop/full_callgraph.dot --remove-builtins --ignore-dir back

# Run the breadth-first-subgraph server
python bfs_server.py

----

Open ~/Desktop/current.dot in the standard Graphviz viewer.
You should now be able to click any node to view its nearby neighbors.
