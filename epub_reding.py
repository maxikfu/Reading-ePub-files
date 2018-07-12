import zipfile
from lxml import etree
from print_tree import print_tree_to_file

# file_name = 'The_Little_Prince.epub'
file_name = 'The_Financier.epub'

# prepare to read from .epub format
zip_content = zipfile.ZipFile(file_name)
ns = {
        'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
        'pkg': 'http://www.idpf.org/2007/opf',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'html': 'http://www.w3.org/1999/xhtml'
    }

# content metafile
txt = zip_content.read('META-INF/container.xml')
tree = etree.fromstring(txt)

container_file_path = tree.xpath('n:rootfiles/n:rootfile/@full-path', namespaces=ns)[0]

# folder where content.opf located and other files should be locating in the same folder
folder_path = container_file_path[:container_file_path.find('content')]

# grab the metadata block from the contents metafile
content_file = zip_content.read(container_file_path)
tree = etree.fromstring(content_file)
# print_tree_to_file(tree, 'out.txt')

metadata = tree.xpath('/pkg:package/pkg:metadata', namespaces=ns)[0]

# grab manifest block from contents metafile. Contains xhtml documents with text
manifest = tree.xpath('/pkg:package/pkg:manifest', namespaces=ns)[0]
manifest_items = manifest.findall('*')

# grab spine, here contains order of xhtml document
spine = tree.xpath('/pkg:package/pkg:spine', namespaces=ns)[0]
spine_content = spine.findall('*')

# retrieving text order from spine
order = []
for itemref in spine_content:
    order.append(itemref.attrib['idref'])

# putting together book text urls
text_files = []
for o in order:
    for item in manifest_items:
        if item.attrib['id'] == o and item.attrib['id'] != 'titlepage':
            text_files.append(folder_path + item.attrib['href'])
# TODO: if <guide> tag exists we need to look into attr text, indicates where actual book text begins, otherwise ...

# reading text files
print(text_files[0])
current_file = text_files[0]
text_file_content = zip_content.read(current_file)
tree = etree.fromstring(text_file_content)
# print_tree_to_file(tree, 'out.txt')
body = tree.xpath('/html:html/html:body', namespaces=ns)[0]
body_children = body.findall('./html:h2', namespaces=ns)
for children in body_children:
    print(children.items())
#print_tree_to_file(body, 'out.txt')
# repackage the data
# res = {}
# for s in ['title', 'language', 'creator', 'date', 'identifier', 'subject']:
#     res[s] = metadata.xpath('dc:%s/text()' % s, namespaces=ns)[0]
# print(res)
