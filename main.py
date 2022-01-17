import sys
import os

from PyPDF2 import PdfFileReader

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")


def extract_information(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()

    txt = f"""
    Information about {pdf_path}: 

    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    """

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
    return filter(lambda f: f[-4:] == '.pdf',   os.listdir())


if __name__ == '__main__':
    for path in get_pdfs():
        print(path)
        extract_information(path)
        print(get_page_content(path, 0))
        # get_all_raw_text(path)
