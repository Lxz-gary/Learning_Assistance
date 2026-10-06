# Utils/excel_exporter.py
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

#导出数据
def export_to_excel(headers, rows, filepath, sheet_name="Sheet1", title=None):
    """
    将数据导出为 Excel 文件（带样式）
    :param headers:  列标题列表，如 ["学号", "考试编号", "科目", ...]
    :param rows:     数据行列表，每行是一个元组/列表，如 [("S0001", "E0982", ...), ...]
    :param filepath: 保存路径，如 "/Users/xxx/成绩.xlsx"
    :param sheet_name: 工作表名
    :param title:    可选，表格顶部的大标题（占据第一行）
    """
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    # ---------- 样式定义 ----------
    header_font  = Font(name="PingFang SC", size=11, bold=True, color="FFFFFF")
    header_fill  = PatternFill("solid", fgColor="4D6BFE")   # DeepSeek 蓝
    header_align = Alignment(horizontal="center", vertical="center")

    body_font    = Font(name="PingFang SC", size=11)
    body_align   = Alignment(horizontal="left", vertical="center")

    title_font   = Font(name="PingFang SC", size=14, bold=True)
    title_align  = Alignment(horizontal="left", vertical="center")

    thin_border  = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    # ---------- 写入数据 ----------
    start_row = 1

    # 可选：大标题
    if title:
        ws.merge_cells(start_row=start_row, start_column=1,
                       end_row=start_row, end_column=len(headers))
        cell = ws.cell(row=start_row, column=1, value=title)
        cell.font = title_font
        cell.alignment = title_align
        ws.row_dimensions[start_row].height = 28
        start_row += 1

    # 表头
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=start_row, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border
    ws.row_dimensions[start_row].height = 22

    # 数据行
    for r, row in enumerate(rows, start=start_row + 1):
        for c, value in enumerate(row, start=1):
            cell = ws.cell(row=r, column=c, value=value)
            cell.font = body_font
            cell.alignment = body_align
            cell.border = thin_border

    # ---------- 自动列宽（按内容估算） ----------
    for col_idx in range(1, len(headers) + 1):
        max_len = len(str(headers[col_idx - 1]))
        for row in rows:
            if col_idx - 1 < len(row):
                max_len = max(max_len, len(str(row[col_idx - 1])))
        # 中文按 2 个宽度算，加 4 的 padding
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len * 1.8 + 4, 50)

    # ---------- 冻结表头 ----------
    ws.freeze_panes = ws.cell(row=start_row + 1, column=1)

    # ---------- 自动筛选 ----------
    last_col = get_column_letter(len(headers))
    ws.auto_filter.ref = f"A{start_row}:{last_col}{start_row + len(rows)}"

    # ---------- 保存 ----------
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb.save(filepath)
    return filepath

#导入数据
def import_from_excel(filepath):
    """
    从 Excel 文件中读取数据
    :param filepath: Excel 文件路径
    :return: (headers, rows) 元组，headers 是列标题列表，rows 是数据行列表
    """
    from openpyxl import load_workbook

    wb = load_workbook(filepath)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        rows.append(row)

    return headers, rows

def default_filename(prefix="导出数据"):
    """生成带时间戳的默认文件名"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.xlsx"