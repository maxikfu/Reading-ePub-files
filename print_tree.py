# Class to print etrees into file.
from lxml import etree


def print_tree_to_file(tree, output_file):
    with open(output_file, 'w') as f:
        f.write(etree.tostring(tree, pretty_print=True).decode('UTF-8'))
