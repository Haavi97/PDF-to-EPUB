from importlib.metadata import metadata
import sys
import os

from PyPDF2 import PdfFileReader
from tqdm import tqdm
from ebooklib import epub

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter

if not sys.warnoptions:
    import warnings
    warnings.simplefilter('ignore')


def extract_information(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()

    txt = f'''
    Information about {pdf_path}: 

    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    '''

    print(txt)
    return information


def get_page_text(pdf_path, n):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        text = pdf.getPage(n).extractText()
    return text


def get_page_content(pdf_path, n):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        text = pdf.getPage(n).getContents()
    return text


def get_all_raw_text(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        n = pdf.getNumPages()
        buffer = ''
        for i in range(1, n):
            buffer += pdf.getPage(i).extractText()
    return buffer


def get_pdfs():
    cwd = os.getcwd()
    os.chdir(cwd + os.sep + 'pdfs')
    pdfs = filter(lambda f: f[-4:] == '.pdf',   os.listdir())
    os.chdir(cwd)
    return pdfs


def default_folders():
    current = os.getcwd() + os.sep + 'pdfs'
    os.mkdir(current) if not os.path.isdir(current) else ''
    current = os.getcwd() + os.sep + 'texts'
    os.mkdir(current) if not os.path.isdir(current) else ''
    current = os.getcwd() + os.sep + 'epubs'
    os.mkdir(current) if not os.path.isdir(current) else ''


def pdf2text(fn, output):
    default_folders()
    caching = True
    rsrcmgr = PDFResourceManager(caching=caching)
    laparams = LAParams()
    laparams.all_texts = True
    imagewriter = None
    outfp = open('texts' + os.sep + output, 'w', encoding='utf-8')
    device = TextConverter(rsrcmgr, outfp, laparams=laparams,
                           imagewriter=imagewriter)
    with open(fn, 'rb') as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pagenos = set()
        maxpages = 0
        password = b''
        rotation = 0
        for page in PDFPage.get_pages(fp, pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            page.rotate = (page.rotate+rotation) % 360
            interpreter.process_page(page)
    device.close()
    outfp.close()


def clean_texts(fn):
    current = os.getcwd() + os.sep + 'cleaned'
    os.mkdir(current) if not os.path.isdir(current) else ''
    with open(fn, 'r', encoding='utf-8') as fi:
        with open('cleaned' + os.sep + fn, 'w', encoding='utf-8') as fo:
            prev = ''
            for l in fi.readlines():
                line = l.strip()
                if line == '':
                    line = '\n'
                if len(prev) < 70:
                    line += '\n'
                fo.write(line)
                prev = line


def create_epub_metadata(book, metadata):
    book.set_identifier(metadata.autor + metadata.title)
    book.set_title(metadata.title)
    book.set_language('en')
    book.add_author(metadata.author)
    if metadata.subject != None:
        book.add_metadata('DC', 'description', metadata.subject)
    if metadata.creator != None:
        book.add_metadata(None, 'meta', '', {
                          'name': 'creator', 'content': metadata.creator})
    if metadata.producer != None:
        book.add_metadata(None, 'meta', '', {
                          'name': 'producer', 'content': metadata.producer})


def create_epub_metadata_from_pdf(book, pdf):
    fp = open(pdf, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    metadata = doc.info[0]
    print('\n'*2, metadata, '\n'*2)
    try:
        book.set_title(metadata['Title'])
        book.set_language('en')
    except KeyError:
        print('Title not found in {}'.format(pdf))
    try:
        book.add_author(metadata['Author'])
    except KeyError:
        print('Author not found in {}'.format(pdf))
    try:
        book.set_identifier(metadata['Author'] + metadata['Title'])
    except KeyError:
        pass
    try:
        book.add_metadata(None, 'meta', '', {
                            'name': 'creator', 'content': metadata['Creator']})
    except KeyError:
        print('Creator not found in {}'.format(pdf))
    try:
        book.add_metadata(None, 'meta', '', {
                        'name': 'producer', 'content': metadata['Producer']})
    except KeyError:
        print('Producer not found in {}'.format(pdf))
    try:
        book.add_metadata(None, 'meta', '', {
                        'name': 'creationDate', 'content': metadata['CreationDate']})
    except KeyError:
        print('CreationDate not found in {}'.format(pdf))
    try:
        book.add_metadata(None, 'meta', '', {
                        'name': 'Keywords', 'content': metadata['Keywords']})
    except KeyError:
        print('Keywords not found in {}'.format(pdf))
    return book


def strip_extension(f):
    return '.'.join(f.split('.')[:-1])


def cd_create(folder):
    os.mkdir(folder) if not os.path.isdir(folder) else ''
    os.chdir(folder)



if __name__ == '__main__':
    file_paths = tqdm(get_pdfs())
    succes = 0
    fail = 0
    for path in file_paths:
        file_paths.set_description('pdf2text: {:<20}'.format(path))
        raw_fn = strip_extension(path)
        fo = raw_fn + '.txt'
        try:
            pdf2text('pdfs' + os.sep + path, fo)
            cwd = os.getcwd()
            cd_create(cwd + os.sep + 'texts')
            try:
                file_paths.set_description(
                    'Cleaning text: {:<20}'.format(path))
                clean_texts(raw_fn + '.txt')
            except UnicodeEncodeError as err:
                print('\n'*2 + '*'*5 +
                      'UnicodeEncodeError cleaning file: ' + path + '\n'*2)
                print(err)
            os.chdir(cwd)
            book = create_epub_metadata_from_pdf(
                epub.EpubBook(), 'pdfs' + os.sep + path)
            cd_create(cwd + os.sep + 'epubs')
            epub.write_epub(raw_fn + '.epub', book)
            os.chdir(cwd)
            succes += 1
        except UnicodeDecodeError as err:
            print('\n'*2 + '*'*5 +
                  'Error executing pdf2text with file: ' + path + '\n'*2)
            print(err)
            fail += 1
    print('\nSuccess: {} Fail: {}'.format(succes, fail))