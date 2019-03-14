"""
    pyexcel_pdfr.pdfr
    ~~~~~~~~~~~~~~~~~~~
    html table reader using messytables

    :copyright: (c) 2015-2017 by Onni Software Ltd & its contributors
    :license: New BSD License
"""
import pyexcel_io.service as service
from pdftables import get_tables
from pyexcel_io._compact import OrderedDict
from pyexcel_io.book import BookReader
from pyexcel_io.sheet import NamedContent, SheetReader


class PdfTable(SheetReader):
    def __init__(
        self,
        sheet,
        auto_detect_int=True,
        auto_detect_float=True,
        auto_detect_datetime=True,
        **keywords
    ):
        SheetReader.__init__(self, sheet, **keywords)
        self.__auto_detect_int = auto_detect_int
        self.__auto_detect_float = auto_detect_float
        self.__auto_detect_datetime = auto_detect_datetime
        self.__table = self._native_sheet.payload
        self.__column_span = {}

    @property
    def name(self):
        return self._native_sheet.name

    def row_iterator(self):
        if hasattr(self.__table, "cell_data"):
            # New style of cell data.
            for row in self.__table.cell_data:
                yield [pdf_cell for pdf_cell in row]
        else:
            for row in self.__table:
                yield [pdf_cell for pdf_cell in row]

    def column_iterator(self, row):
        index = 0
        for cell in row:
            # generate '' due to previous rowspan
            while index in self.__column_span:
                # and keep generating '' if next index is in the list
                self.__column_span[index] -= 1
                if self.__column_span[index] == 0:
                    del self.__column_span[index]
                yield ""
                index += 1

            if not hasattr(cell, "topleft"):
                yield cell
                index += 1
                continue

            col_span, row_span = cell.size
            yield self.__convert_cell(cell.content)
            if row_span > 1:
                # generate '' due to colspan
                if col_span > 1:
                    for offset in range(row_span):
                        if offset > 0:
                            # for next cell, give full col span
                            self.__column_span[index + offset] = col_span
                        else:
                            # for current cell, give -1 because it has been
                            # yielded
                            self.__column_span[index + offset] = col_span - 1
                else:
                    # no col span found, so just repeat in the same row
                    for _ in range(row_span - 1):
                        yield ""
                        index += 1
            else:
                if col_span > 1:
                    self.__column_span[index] = col_span - 1
            # next index
            index += 1

    def __convert_cell(self, cell_text):
        ret = None
        if self.__auto_detect_int:
            ret = service.detect_int_value(cell_text)
        if ret is None and self.__auto_detect_float:
            ret = service.detect_float_value(cell_text)
            shall_we_ignore_the_conversion = (
                ret in [float("inf"), float("-inf")]
            ) and self.__ignore_infinity
            if shall_we_ignore_the_conversion:
                ret = None
        if ret is None and self.__auto_detect_datetime:
            ret = service.detect_date_value(cell_text)
        if ret is None:
            ret = cell_text
        return ret


class PdfFile(BookReader):
    def __init__(self):
        BookReader.__init__(self)
        self._file_handle = None

    def open(self, file_name, **keywords):
        BookReader.open(self, file_name, **keywords)
        self._load_from_file()

    def open_stream(self, file_stream, **keywords):
        BookReader.open_stream(self, file_stream, **keywords)
        self._load_from_memory()

    def read_all(self):
        result = OrderedDict()
        for sheet in self._native_book:
            result.update(self.read_sheet(sheet))
        return result

    def read_sheet(self, native_sheet):
        sheet = PdfTable(native_sheet, **self._keywords)
        return {sheet.name: sheet.to_array()}

    def _load_from_file(self):
        self._file_handle = open(self._file_name, "rb")
        self._native_book = self._parse_pdf(self._file_handle)

    def _load_from_memory(self):
        self._native_book = self._parse_pdf(self._file_stream)

    def _parse_pdf(self, file_handle):
        for table in get_tables(file_handle):
            name = "Table {0} of {1} on page {2} of {3}".format(
                table.table_number_on_page,
                table.total_tables_on_page,
                table.page_number,
                table.total_pages,
            )
            yield NamedContent(name, table)

    def close(self):
        if self._file_handle:
            self._file_handle.close()
