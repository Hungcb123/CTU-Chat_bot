with open("data/markdown/MucHocPhi.md", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("| 1 | Nuôi trồng thủy sản | | | 935 | | 1.211 | 1.309 | 1.284 | 1.422 | 1.564 |", "| 1 | Nuôi trồng thủy sản | 935 | 935 | 935 | | 1.211 | 1.309 | 1.284 | 1.422 | 1.564 |")
content = content.replace("| 2 | Công nghệ sinh học | | | 935 | | 1.191 | 1.286 | 1.230 | 1.363 | 1.499 |", "| 2 | Công nghệ sinh học | 935 | 935 | 935 | | 1.191 | 1.286 | 1.230 | 1.363 | 1.499 |")

with open("data/markdown/MucHocPhi.md", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed!")
