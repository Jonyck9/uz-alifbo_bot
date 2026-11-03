from pathlib import Path

from docx import Document
from openpyxl import load_workbook

from converter import convert


def _translate_paragraphs(paragraphs, source, target):
    for paragraph in paragraphs:
        if paragraph.text:
            paragraph.text = convert(paragraph.text, source, target)


def _translate_table(table, source, target, seen_cells):
    for row in table.rows:
        for cell in row.cells:
            cell_id = id(cell._tc)
            if cell_id in seen_cells:
                continue
            seen_cells.add(cell_id)
            _translate_paragraphs(cell.paragraphs, source, target)
            for nested_table in cell.tables:
                _translate_table(nested_table, source, target, seen_cells)


def translate_document(input_path, output_path, source, target):
    input_path = Path(input_path)
    if input_path.suffix.lower() == '.docx':
        document = Document(input_path)
        _translate_paragraphs(document.paragraphs, source, target)
        seen_cells = set()
        for table in document.tables:
            _translate_table(table, source, target, seen_cells)
        for section in document.sections:
            _translate_paragraphs(section.header.paragraphs, source, target)
            _translate_paragraphs(section.footer.paragraphs, source, target)
            for table in section.header.tables + section.footer.tables:
                _translate_table(table, source, target, seen_cells)
        document.save(output_path)
        return

    workbook = load_workbook(input_path)
    for worksheet in workbook.worksheets:
        for row in worksheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.data_type != 'f':
                    cell.value = convert(cell.value, source, target)
    workbook.save(output_path)
