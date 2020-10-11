"""
    pyexcel_pdfr.pdfr
    ~~~~~~~~~~~~~~~~~~~
    pdf table using camelot

    :copyright: (c) 2015-2020 by Onni Software Ltd & its contributors
    :license: New BSD License
"""
import camelot
from pyexcel_io.plugin_api import ISheet, IReader, NamedContent


class PdfTable(ISheet):
    def __init__(
        self,
        table,
        auto_detect_int=True,
        auto_detect_float=True,
        auto_detect_datetime=True,
    ):
        self.__auto_detect_int = auto_detect_int
        self.__auto_detect_float = auto_detect_float
        self.__auto_detect_datetime = auto_detect_datetime
        self.__table = table
        self.__column_span = {}

    def row_iterator(self):
        yield from self.__table.rows

    def column_iterator(self, row):
        for cell in row:
            yield cell


class PdfFile(IReader):
    def __init__(self, file_name, _, **keywords):
        self.tables = camelot.read_pdf(file_name)
        self.content_array = [
            NamedContent(f"pyexcel_sheet_{index}", table)
            for index, table in enumerate(self.tables)
        ]
        self._keywords = keywords

    def read_sheet(self, native_sheet_index):
        table = self.content_array[native_sheet_index].payload
        sheet = PdfTable(table, **self._keywords)
        return sheet

    def close(self):
        pass
