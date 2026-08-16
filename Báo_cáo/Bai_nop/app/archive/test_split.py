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
        
        # Sample 20 random docs
        samples = random.sample(docs, min(20, len(docs)))
        
        for i, doc in enumerate(samples):
            print(f"--- Document {i+1} ---")
            print(f"ID: {doc.id}")
            print(f"Metadata: {doc.metadata_json}")
            print(f"Length: {len(doc.content)} chars")
            print(f"Content Preview:\n{doc.content[:300]}...")
            print("-----------------------\n")
            
if __name__ == "__main__":
    survey()
