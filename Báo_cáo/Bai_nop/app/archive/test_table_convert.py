import re

def convert_tables_to_list(markdown_text):
    # Regex to find markdown tables
    # A markdown table has lines with | characters.
    # We can find blocks of consecutive lines starting/ending with | or containing multiple |
    
    lines = markdown_text.split('\n')
    new_lines = []
    
    in_table = False
    table_headers = []
    
    for line in lines:
        is_table_row = '|' in line and len(line.strip()) > 0
        
        if is_table_row:
            cells = [cell.strip() for cell in line.split('|')][1:-1] # assuming standard format | a | b |
            
            if not in_table:
                # First row of a table is usually the header
                table_headers = cells
                in_table = True
                new_lines.append("\n[BẢNG DỮ LIỆU ĐÃ CHUYỂN ĐỔI]")
            else:
                # Is it the separator line? |---|---|
                if all(re.match(r'^[\-\s:]+$', cell) for cell in cells if cell):
                    continue # Skip separator
                
                # Data row
                row_str = " - "
                for i, cell in enumerate(cells):
                    header = table_headers[i] if i < len(table_headers) else f"Cột {i+1}"
                    row_str += f"{header}: {cell} | "
                new_lines.append(row_str)
        else:
            in_table = False
            new_lines.append(line)
            
    return '\n'.join(new_lines)

sample = """
Dưới đây là danh sách học bổng:
| MSSV | Họ Tên | Lớp | Số Tiền |
|---|---|---|---|
| B2401 | Nguyễn Văn A | DI22 | 5.000.000 |
| B2402 | Trần Thị B | KT22 | 4.000.000 |

Chúc mừng các bạn!
"""

print(convert_tables_to_list(sample))
