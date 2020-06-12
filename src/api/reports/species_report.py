import shutil
import tempfile
import uuid

from pathlib import Path

from django.conf import settings
from openpyxl import load_workbook
from openpyxl.utils import rows_from_range


TEMPLATE_PATH = f"{settings.BASE_DIR}/templates/scl_report_mvp.xlsx"

DATA_CELL_MAP = {
    "species": "B3",
    "report_date": "B4",
    "country": "B5",
    "total_protected": "D12",
    "table_data": "B8:D11",  # 2D list (shape: 4 x 3)
}


def open_new_template(template):
    tmp_dir = tempfile.gettempdir()
    tmp_file_name = f"{uuid.uuid4()}.xlsx"
    tmp_file_path = Path(tmp_dir, tmp_file_name)
    shutil.copyfile(template, tmp_file_path)
    return tmp_file_path


def insert_range(sheet, range_str, data):
    cells = rows_from_range(range_str)
    for y, rows in enumerate(cells):
        for x, col in enumerate(rows):
            sheet[col] = data[y][x]


def generate(data):
    report_path = open_new_template(TEMPLATE_PATH)
    workbook = load_workbook(filename=report_path)
    sheet = workbook.active

    for key, value in data.items():
        coord = DATA_CELL_MAP.get(key)
        if not coord:
            continue

        if ":" in coord:
            insert_range(sheet, coord, value)
        else:
            sheet[coord] = value

    workbook.save(filename=report_path)
    return report_path
