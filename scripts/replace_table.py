import sys

with open("data/markdown/MucHocPhi.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_content = """#### I. Học phí cố định theo khóa học (triệu đồng/năm học) - Chương trình chất lượng cao
| TT | Ngành | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Công nghệ thông tin | 25 | 26 | 28 | 30 | 33 | 36 | 36 | 40 | 44 |
| 2 | Kinh doanh quốc tế | 22 | 24 | 27 | 30 | 33 | 36 | 36 | 40 | 44 |
| 3 | Công nghệ kỹ thuật hóa học | 25 | 25 | 28 | 30 | 33 | 36 | 36 | 40 | 44 |
| 4 | Kỹ thuật điện | 25 | 25 | 28 | 30 | 33 | 33 | 36 | 40 | 44 |
| 5 | Công nghệ thực phẩm | 25 | 25 | 28 | 30 | 33 | 33 | 36 | 40 | 44 |
| 6 | Ngôn ngữ Anh | 22 | 24 | 27 | 30 | 33 | 36 | 36 | 40 | 44 |
| 7 | Tài chính – Ngân hàng | | 24 | 27 | 30 | 33 | 33 | 33 | 40 | 44 |
| 8 | Kỹ thuật xây dựng | | 26 | 28 | 30 | 33 | 33 | 33 | 40 | 44 |
| 9 | Quản trị kinh doanh | | | | | 33 | 33 | 33 | 40 | 44 |
| 10 | QT DV Du lịch và Lữ hành | | | | | 33 | 33 | 33 | 40 | 44 |
| 11 | Kỹ thuật phần mềm | | | | | 33 | 33 | 33 | 40 | 44 |
| 12 | KT điều khiển và TĐH | | | | | | 33 | 33 | 37 | 41 |
| 13 | Hệ thống thông tin | | | | | | 33 | 33 | 40 | 44 |
| 14 | Mạng máy tính và truyền thông dữ liệu | | | | | | | | 40 | 44 |
| 15 | Thú y | | | | | | | | 40 | 44 |
| 16 | Bảo vệ thực vật | | | | | | | | | 44 |
| 17 | Kỹ thuật cơ khí | | | | | | | | | 44 |

#### I. Học phí cố định theo khóa học (triệu đồng/năm học) - Chương trình tiên tiến
| TT | Ngành | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Nuôi trồng thủy sản | | | | | 33 | 36 | 36 | 40 | 44 |
| 2 | Công nghệ sinh học | | | | | 33 | 36 | 36 | 36 | 44 |

#### II. Học phí cố định tính theo tín chỉ (1.000 đồng/tín chỉ) - Mức học phí khối đại cương chung
| Khối kiến thức | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
|---|---|---|---|---|---|---|---|---|---|
| Mức học phí của khối kiến thức đại cương chung (tất cả các ngành) | 265 | 280 | 280 | 280 | 352 | 441 | 550 | 630 | 695 |

#### II. Học phí cố định tính theo tín chỉ (1.000 đồng/tín chỉ) - Chương trình chất lượng cao
| TT | Ngành | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Công nghệ thông tin | 882 | 914 | 989 | 1.064 | 1.161 | 1.254 | 1.181 | 1.308 | 1.438 |
| 2 | Kinh doanh quốc tế | 770 | 839 | 951 | 1.064 | 1.161 | 1.254 | 1.230 | 1.363 | 1.499 |
| 3 | Công nghệ kỹ thuật hóa học | 882 | 876 | 989 | 1.064 | 1.161 | 1.254 | 1.181 | 1.308 | 1.438 |
| 4 | Kỹ thuật điện | 882 | 876 | 989 | 1.064 | 1.161 | 1.142 | 1.181 | 1.308 | 1.438 |
| 5 | Công nghệ thực phẩm | 882 | 876 | 989 | 1.064 | 1.161 | 1.142 | 1.181 | 1.308 | 1.438 |
| 6 | Ngôn ngữ Anh | 707 | 771 | 875 | 980 | 1.068 | 1.152 | 1.127 | 1.248 | 1.372 |
| 7 | Tài chính – Ngân hàng | | 839 | 951 | 1.064 | 1.161 | 1.142 | 1.118 | 1.363 | 1.499 |
| 8 | Kỹ thuật xây dựng | | 876 | 989 | 1.064 | 1.161 | 1.142 | 1.073 | 1.308 | 1.438 |
| 9 | Quản trị kinh doanh | | | | | 1.161 | 1.142 | 1.118 | 1.363 | 1.499 |
| 10 | QT DV Du lịch và Lữ hành | | | | | 1.161 | 1.142 | 1.118 | 1.363 | 1.499 |
| 11 | Kỹ thuật phần mềm | | | | | 1.161 | 1.142 | 1.073 | 1.308 | 1.438 |
| 12 | KT điều khiển và TĐH | | | | | | 1.142 | 1.118 | 1.251 | 1.386 |
| 13 | Hệ thống thông tin | | | | | | | 1.118 | 1.308 | 1.438 |
| 14 | Mạng máy tính và truyền thông dữ liệu | | | | | | | | 1.308 | 1.438 |
| 15 | Thú y | | | | | | | | 1.412 | 1.553 |
| 16 | Bảo vệ thực vật | | | | | | | | | 1.438 |
| 17 | Kỹ thuật cơ khí | | | | | | | | | 1.438 |

#### II. Học phí cố định tính theo tín chỉ (1.000 đồng/tín chỉ) - Chương trình tiên tiến
| TT | Ngành | K44 | K45 | K46 | K47 | K48 | K49 | K50 | K51 | K52 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Nuôi trồng thủy sản | | | 935 | | 1.211 | 1.309 | 1.284 | 1.422 | 1.564 |
| 2 | Công nghệ sinh học | | | 935 | | 1.191 | 1.286 | 1.230 | 1.363 | 1.499 |
"""

# Replace lines 359 to 409
# Array is 0-indexed. line 360 is index 359. line 410 is index 409.
del lines[359:410]

lines.insert(359, new_content)

with open("data/markdown/MucHocPhi.md", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Done replacing.")
