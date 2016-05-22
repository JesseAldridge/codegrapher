import os
import re

import click

from codegrapher.graph import FunctionGrapher
from codegrapher.parser import FileObject


@click.command()
@click.argument('code', type=click.Path())
@click.option('-r', '--recursive', default=False, is_flag=True,
              help='Treat code argument as a directory and parse all files in directory, recursively')
@click.option('--printed', default=False, is_flag=True, help='Pretty prints the call tree for each class in the file')
@click.option('--use-cg-ignore', default=False, is_flag=True, help='Use a .cg_ignore file to ignore functions in call tree')
@click.option('--ignore-dir', help='Ignore a directory', multiple=True)
@click.option('--remove-builtins', default=False, is_flag=True, help='Removes builtin functions from call trees')
@click.option('--output', help='Graphviz output file name')
@click.option('--output-format', default='pdf', help='File type for graphviz output file')
def cli(code, recursive, printed, use_cg_ignore, ignore_dir, remove_builtins, output, output_format):
    """
    Parses a file.
    codegrapher [file_name]
    """
    file_list = []
    if recursive:
        exclude = {'site-packages'} | set(ignore_dir)
        for dirpath, dirnames, filenames in os.walk(code, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in exclude]
            for filename in filenames:
                if re.search(r'\.py$', filename):
                    file_list.append(os.sep.join([dirpath, filename]))
    else:
        file_list.append(code)

    graph = None
    for file_name in file_list:
        print 'file_name:', file_name
        file_object = FileObject(file_name)
        file_object.visit()
        if remove_builtins:
            file_object.remove_builtins()
        if use_cg_ignore:
            file_object.add_ignore_file()
            file_object.ignore_functions()
        if printed:
            click.echo('Classes in file {}:'.format(file_name))
            for class_object in file_object.classes:
                click.echo('=' * 80)
                click.echo(class_object.name)
                click.echo(class_object.pprint())
                click.echo('')
        if output:
            try:
                graph.add_file_to_graph(file_object)
            except AttributeError:
                graph = FunctionGrapher()
                graph.add_file_to_graph(file_object)
    if output:
        print 'rendering...'
        graph.name = output
        graph.format = output_format
        graph.render()
