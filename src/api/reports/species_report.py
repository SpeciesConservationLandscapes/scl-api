import shutil
import tempfile
import uuid
from collections.abc import Sequence
from pathlib import Path

from django.conf import settings
from openpyxl import load_workbook
from openpyxl.utils import coordinate_to_tuple, get_column_letter, rows_from_range

TEMPLATE_PATH = f"{settings.BASE_DIR}/templates/scl_report_mvp.xlsx"

DATA_CELL_MAP = {
    "country summary": {
        "species": "B3",
        "report_date": "B4",
        "country": "B5",
        "total_protected": "D12",
        "table_data": "B8:D11",  # 2D list (shape: 4 x 3)
    },
    "landscapes over time": {"chart_data": "A2",},
}


def is_sequence(val):
    return isinstance(val, Sequence) and not isinstance(val, str)


def open_new_template(template):
    tmp_dir = tempfile.gettempdir()
    tmp_file_name = f"{uuid.uuid4()}.xlsx"
    tmp_file_path = Path(tmp_dir, tmp_file_name)
    shutil.copyfile(template, tmp_file_path)
    return tmp_file_path


def rows_from_data(coord, data):
    p0, p1 = coordinate_to_tuple(coord)
    if not data:
        return []

    if is_sequence(data[0]):
        w = len(data[0])
    else:
        w = 1

    start_letter = get_column_letter(p1)
    end_letter = get_column_letter(p1 + w - 1)

    return rows_from_range(f"{start_letter}{p0}:{end_letter}{p0 + h - 1}")


def insert_range(sheet, range_str, data):
    if ":" in range_str:
        cells = rows_from_range(range_str)
    else:
        cells = rows_from_data(range_str, data)

    for y, rows in enumerate(cells):
        for x, col in enumerate(rows):
            sheet[col] = data[y][x]


def generate(data):
    report_path = open_new_template(TEMPLATE_PATH)
    workbook = load_workbook(filename=report_path)
    sheet = workbook.active

    for sheet_name, sheet_data in data.items():
        sheet = workbook[sheet_name]
        sheet_map = DATA_CELL_MAP.get(sheet_name)
        if sheet_map is None:
            break

        for key, value in sheet_data.items():
            coord = sheet_map.get(key)
            if not coord:
                continue

            if is_sequence(value):
                insert_range(sheet, coord, value)
            else:
                sheet[coord] = value

    workbook.save(filename=report_path)
    return report_path
