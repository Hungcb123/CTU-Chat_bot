import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SyncSessionLocal
from models.schema import ParentDocument
import re

def survey():
    with SyncSessionLocal() as session:
        docs = session.query(ParentDocument).all()
        
        table_chunks = 0
        broken_tables = 0
        
        for doc in docs:
            content = doc.content
            # Check if this chunk has table rows (lines starting/ending with | or having multiple |)
            lines = content.strip().split('\n')
            table_lines = [l for l in lines if l.strip().startswith('|') or l.strip().count('|') >= 2]
            
            if table_lines:
                table_chunks += 1
                # A proper markdown table chunk should ideally have a header and a separator line like |---|---|
                # If a chunk consists mostly of table rows but no separator line, it's a broken table chunk
                has_separator = any(re.match(r'^[|\s\-:]+$', l.strip()) for l in table_lines)
                
                # Check if it looks like a mid-table fragment
                if len(table_lines) > 2 and not has_separator:
                    broken_tables += 1
                    print(f"--- BROKEN TABLE FOUND ---")
                    print(f"ID: {doc.id}")
                    print(f"Source: {doc.metadata_json.get('source', 'Unknown')}")
                    print(f"Length: {len(content)}")
                    print(f"Content:\n{content[:500]}...\n-------------------\n")

        print(f"Total chunks with tables: {table_chunks}")
        print(f"Potentially broken tables: {broken_tables}")
        
if __name__ == "__main__":
    survey()
