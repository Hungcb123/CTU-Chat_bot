#!/usr/bin/env python3
import os
import glob
import re

def remove_yaml_frontmatter(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to match YAML frontmatter
    # Matches `---` at the start of the string, followed by any characters
    # (non-greedy), followed by `---` and optional newlines (handles both LF and CRLF).
    pattern = re.compile(r'^---\r?\n.*?\r?\n---\r?\n*', re.DOTALL)
    
    new_content, count = pattern.subn('', content)
    
    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    import sys
    # Target directory
    if len(sys.argv) > 1:
        md_dir = os.path.abspath(sys.argv[1])
    else:
        md_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'markdown'))
    
    if not os.path.exists(md_dir):
        print(f"Directory not found: {md_dir}")
        return

    md_files = glob.glob(os.path.join(md_dir, '*.md'))
    processed = 0
    modified = 0

    for file_path in md_files:
        processed += 1
        if remove_yaml_frontmatter(file_path):
            modified += 1
            print(f"Removed frontmatter from: {os.path.basename(file_path)}")

    print(f"\nDone! Processed {processed} files, removed frontmatter from {modified} files.")

if __name__ == '__main__':
    main()
