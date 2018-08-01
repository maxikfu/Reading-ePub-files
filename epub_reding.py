import zipfile
from lxml import etree
from print_tree import print_tree_to_file


class ePub_reader:

    @staticmethod
    def get_book_dict(file_name):  # returns dictionary with book content
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
        book = {}
        chapters_order = []
        unknown_chapter_counter = 1
        for current_file in text_files:
            chapters = []
            chapter_borders = []
            # print(current_file)
            text_file_content = zip_content.read(current_file)
            tree = etree.fromstring(text_file_content)

            body = tree.xpath('/html:html/html:body', namespaces=ns)[0]
            print_tree_to_file(tree, 'out.txt')
            body_children = body.findall('./html:h2', namespaces=ns)
            left_border = None
            i = 0
            # calculating chapter borders
            for children in body_children:
                if children.text:
                    chapters.append(children.text)
                    chapters_order.append(children.text)
                    if left_border is None:
                        chapter_borders.append([body.index(children) + 1])
                        left_border = 3
                        i += 1
                    else:
                        chapter_borders[i-1].append(body.index(children)-1)
                        chapter_borders.append([body.index(children) + 1])
                        left_border = body.index(children) + 1
                        i += 1
            # TODO: what if there are no chapters in the document: we read entire body tag, but onlu <p> tags I guess
            if chapters:
                chapter_borders[len(chapter_borders)-1].append(len(body)-1)
                for chapter, border in zip(chapters, chapter_borders):
                    # print(chapter)
                    if chapter in book:
                        print('Error, chapter number repeats!!!!')
                    else:
                        book[chapter] = []  # inside chapter we keep text in paragraphs
                        for i in range(border[0], border[1]+1):  # collecting paragraphs together
                            book[chapter].append(body[i].text)
            else:  # unknown chapters
                paragraphs = body.findall('./html:p', namespaces=ns)
                if len(paragraphs) > 6:  # more than 6 p maybe still chapter with out name
                    chapter = 'UNKNOWN_CHAPTER_' + str(unknown_chapter_counter)
                    chapters_order.append(chapter)
                    unknown_chapter_counter += 1
                    book[chapter] = []
                    for p in paragraphs:
                        book[chapter].append(p.text)
        book['chapters'] = chapters_order
        # repackage the data
        for s in ['title', 'language', 'creator', 'date', 'identifier', 'subject']:
            book[s] = metadata.xpath('dc:%s/text()' % s, namespaces=ns)[0]
        return book
