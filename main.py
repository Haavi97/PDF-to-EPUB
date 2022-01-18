import sys
import os

from PyPDF2 import PdfFileReader

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


if __name__ == '__main__':
    for path in get_pdfs():
        print(path)
        fo = path[:-4] + '.txt'
        try:
            pdf2text('pdfs' + os.sep + path, fo)
            cwd = os.getcwd()
            os.chdir(cwd + os.sep + 'texts')
            try:
                clean_texts(path[:-4] + '.txt')
            except UnicodeEncodeError as err:
                print('UnicodeEncodeError cleaning file: ' + path)
                print(err)
            os.chdir(cwd)
        except UnicodeDecodeError as err:
            print('Error executing pdf2text with file: ' + path)
            print(err)
