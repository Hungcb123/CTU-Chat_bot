import re

def manual_markdown_splitter(text, strip_headers=False):
    lines = text.split('\n')

    chunk=[]
    current_content = []

    current_state = {
        "Header_1_QuyetDinh" : None,
        "Header_2_ChuyenMuc" : None,
        "Header_3_NguoiKy" : None
    }

    def save_chunk():
        
        