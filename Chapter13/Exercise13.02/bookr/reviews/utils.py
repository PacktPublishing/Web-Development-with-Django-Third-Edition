from xlsxwriter.utility import xl_rowcol_to_cell, xl_range

def average_rating(rating_list):
    if not rating_list:
        return 0

    return round(sum(rating_list) / len(rating_list))

def format_workbook(workbook, rows, format_settings,
    header, col_formats, column_widths, footer_avg={}):

    worksheet = workbook.add_worksheet('Review Summary')

    # Create format objects
    formats = {format_id: workbook.add_format(format_set)
               for format_id, format_set in format_settings.items()}

    for col_range, width in column_widths:
        worksheet.set_column(col_range, width)

    # Write header
    worksheet.write_row('A1', header, formats['header'])
    for col_num, cell_data in enumerate(header):
        worksheet.write(0, col_num, cell_data,
        formats['header'])

    # Write data
    for row_num, row in enumerate(rows):
        if not row:
            continue
        for col_num, col in enumerate(list(row.values())):
            worksheet.write(row_num+1, col_num, col,
                            formats[col_formats[col_num]])

    # Add footer with average rating
    if footer_avg:
        row_id = len(rows) + 1
        col_id = header.index(footer_avg['id'])
        col_label_id = col_id - 1 if col_id > 0 else len(col_formats)
        worksheet.write(
                        row_id,
                        col_label_id,
                        f"{footer_avg['label']}:", formats['footer'])
        avg_cell = xl_rowcol_to_cell(len(rows)+1, col_id)
        avg_range = xl_range(1, col_id, row_id-1, col_id)
        worksheet.write_formula(avg_cell, f"=AVERAGE({avg_range})")

    return workbook
