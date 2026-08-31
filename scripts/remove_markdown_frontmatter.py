import os
import re
from pathlib import Path

DIRECTORY = Path("/mnt/d/Project/Chatbot/data/markdown_graph")

def remove_frontmatter(content: str) -> tuple[str, bool]:
    # Match YAML frontmatter at the very beginning of the document
    # ^---\s*\n.*?\n---\s*\n*
    pattern = r"^---\s*\r?\n.*?\r?\n---\s*\r?\n*"
    match = re.match(pattern, content, re.DOTALL)
    if match:
        new_content = content[match.end():]
        return new_content, True
    return content, False

def main():
    if not DIRECTORY.exists():
        print(f"Directory not found: {DIRECTORY}")
        return

    md_files = sorted(DIRECTORY.glob("*.md"))
    print(f"Found {len(md_files)} markdown files in {DIRECTORY}")

    modified_count = 0
    skipped_count = 0

    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            new_content, changed = remove_frontmatter(content)
            if changed:
                file_path.write_text(new_content, encoding="utf-8")
                modified_count += 1
            else:
                skipped_count += 1
                print(f"[SKIPPED - No frontmatter]: {file_path.name}")
        except Exception as e:
            print(f"[ERROR]: {file_path.name}: {e}")

    print("\n" + "="*50)
    print(f"Total files: {len(md_files)}")
    print(f"Successfully cleaned: {modified_count}")
    print(f"Skipped (no frontmatter): {skipped_count}")
    print("="*50)

if __name__ == "__main__":
    main()
