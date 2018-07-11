import zipfile
from lxml import etree
from print_tree import print_tree_to_file

# file_name = 'The_Little_Prince.epub'
file_name = 'Martin_Eden.epub'

# prepare to read from .epub format
zip_content = zipfile.ZipFile(file_name)
ns = {
        'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
        'pkg': 'http://www.idpf.org/2007/opf',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
#
# for content_fname in zip_content.namelist():
#     print(content_fname)

# content metafile
txt = zip_content.read('META-INF/container.xml')
tree = etree.fromstring(txt)

container_file_path = tree.xpath('n:rootfiles/n:rootfile/@full-path', namespaces=ns)[0]

# grab the metadata block from the contents metafile
content_file = zip_content.read(container_file_path)
tree = etree.fromstring(content_file)
# with open('out.txt', 'w') as f:
#     f.write(etree.tostring(tree, pretty_print=True).decode('UTF-8'))
metadata = tree.xpath('/pkg:package/pkg:metadata', namespaces=ns)[0]

# grab manifest block from contents metafile. Contains xhtml documents with text
manifest = tree.xpath('/pkg:package/pkg:manifest', namespaces=ns)[0]

# grab spine, here contains order of xhtml document
spine = tree.xpath('/pkg:package/pkg:spine', namespaces=ns)[0]
print_tree_to_file(tree, 'out.txt')
print(spine.xpath('/pkg:package/pkg:spine/pkg:itemref/@idref', namespaces=ns)[0])
# repackage the data
# res = {}
# for s in ['title', 'language', 'creator', 'date', 'identifier', 'subject']:
#     res[s] = metadata.xpath('dc:%s/text()' % s, namespaces=ns)[0]
# print(res)
