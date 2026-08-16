import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SyncSessionLocal
from models.schema import ParentDocument
import random

def survey():
    with SyncSessionLocal() as session:
        docs = session.query(ParentDocument).all()
        print(f"Total documents: {len(docs)}")
        
        if not docs:
            print("No documents found in database.")
            return

        # Simple statistics
        lengths = [len(d.content) for d in docs]
        avg_len = sum(lengths) / len(lengths)
        max_len = max(lengths)
        min_len = min(lengths)
        short_docs = sum(1 for l in lengths if l < 100)
        
        print(f"Average length: {avg_len:.2f} chars")
        print(f"Max length: {max_len} chars")
        print(f"Min length: {min_len} chars")
        print(f"Documents under 100 chars: {short_docs} ({short_docs/len(docs)*100:.1f}%)\n")
        
        # Sample 10 random docs
        samples = random.sample(docs, min(10, len(docs)))
        
        for i, doc in enumerate(samples):
            print(f"--- Sample {i+1} ---")
            print(f"ID: {doc.id}")
            print(f"Metadata: {doc.metadata_json}")
            print(f"Length: {len(doc.content)} chars")
            content_preview = doc.content.replace('\n', '\\n')[:300]
            print(f"Content Preview: {content_preview}...")
            print("-----------------------\n")
            
if __name__ == "__main__":
    survey()
