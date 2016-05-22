import os, shlex, collections, itertools, random

import requests
import flask
from flask import request

import bfs_rewrite

FULL_CALLGRAPH_PATH = os.path.expanduser('~/Desktop/full_callgraph.dot')
PARTIAL_CALLGRAPH_PATH = os.path.expanduser('~/Desktop/current.dot')

def run_server():
  app = flask.Flask(__name__)

  @app.route('/')
  def render():
    rewrite_dotfile(request.args['starting_from'])
    return 'ok'

  rewrite_dotfile(central_name=None)
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=port==5000)


def rewrite_dotfile(central_name):
  name_to_node = bfs_rewrite.parse_digraph(FULL_CALLGRAPH_PATH)
  central_name = central_name or name_to_node.keys()[0]
  to_show = bfs_rewrite.breadth_first(name_to_node[central_name], steps=64)
  write_digraph(to_show)


def each_neighbor_once(neighbors):
  seen = set()
  for neighbor in neighbors:
    if neighbor.func_name in seen:
      continue
    yield neighbor
    seen.add(neighbor.func_name)


def write_digraph(to_show):
  lines = ['digraph G {', 'rankdir="LR";']

  for from_ in to_show.itervalues():
    req = requests.Request(
      'GET', 'http://localhost:5000', params={"starting_from": from_.func_name})
    prepped = req.prepare()
    lines.append('"{}" [ URL="{}" ]'.format(from_.func_name, prepped.url))

  colors = itertools.cycle([
      '#ff0000', 'orange', '#00aaaa', '#0000ff', '#00aa00', '#888800',
      '#aa00aa'])

  for from_ in to_show.itervalues():
    for to in each_neighbor_once(from_.calls):
      if to.func_name not in to_show:
        continue
      edge_str = ' -> '.join('"{}"'.format(s) for s in (from_.func_name, to.func_name))
      color = colors.next()
      lines.append('{} [{}]'.format(edge_str, 'color="{}"'.format(color)))

  lines.append('}')
  text = '\n'.join(lines)
  with open(PARTIAL_CALLGRAPH_PATH, 'w') as f:
    f.write(text)

if __name__ == '__main__':
  run_server()
