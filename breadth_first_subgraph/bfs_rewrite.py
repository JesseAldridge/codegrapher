import shlex, collections

class FuncNode:
  def __init__(self, func_name):
    self.func_name = func_name
    self.callers = []
    self.calls = []

def parse_digraph(path):
  # Read the dot file call graph and create FuncNode instances.

  with open(path) as f:
    text = f.read()
  lines = text.splitlines()[1:-1]
  name_to_node = {}
  for line in lines:
    if ' -> ' not in line:
      continue
    from_name, _, to_name = shlex.split(line)
    if from_name not in name_to_node:
      name_to_node[from_name] = FuncNode(from_name)
    if to_name not in name_to_node:
      name_to_node[to_name] = FuncNode(to_name)
    from_, to = name_to_node[from_name], name_to_node[to_name]
    from_.calls.append(to)
    to.callers.append(from_)
  return name_to_node

def breadth_first(central_node, steps):
  # Take N steps through the call graph and select those nodes.

  to_show = collections.OrderedDict()
  to_show[central_node.func_name] = central_node
  it = to_show.itervalues()
  for from_ in to_show.itervalues():
    for neighbor in from_.calls + from_.callers:
      if neighbor.func_name in to_show:
        continue
      to_show[neighbor.func_name] = neighbor
      if len(to_show) == steps:
        return to_show
  return to_show

if __name__ == '__main__':
  name_to_node = parse_digraph('test_data/test.dot')
  assert len(name_to_node) == 4

  to_show = breadth_first(name_to_node[name_to_node.keys()[0]], 8)
  assert len(to_show) == 4

  name_to_node = parse_digraph('test_data/test.dot')
  assert len(name_to_node) == 4

  to_show = breadth_first(name_to_node[name_to_node.keys()[0]], 8)
  assert len(to_show) == 4
