import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.database import SessionLocal
from app.services.import_service import ImportService

def import_knowledge(file_path):
    db = SessionLocal()
    try:
        service = ImportService(db)
        stats = service.process_import(file_path)
        
        print("TARS Personal Knowledge Import\n")
        print(f"Source:\n{os.path.basename(file_path)}\n")
        print(f"Profile:\n  Imported: {stats.get('categories', {}).get('profile', 0)}\n")
        print(f"Education:\n  Imported: {stats.get('categories', {}).get('education', 0)}\n")
        print(f"Career:\n  Imported: {stats.get('categories', {}).get('career', 0)}\n")
        print(f"Skills:\n  Imported: {stats.get('categories', {}).get('skills', 0)}\n")
        print(f"Certifications:\n  Imported: {stats.get('categories', {}).get('certifications', 0)}\n")
        print(f"Evidence:\n  Imported: {stats.get('categories', {}).get('evidence', 0)}\n")
        
        print(f"Duplicates:\n  {stats.get('duplicates', 0)}")
        print(f"Confidential items:\n  {stats.get('review_required', 0)}")
        print(f"Validation errors:\n  {stats.get('validation_errors', 0)}")
        print(f"\nStatus:\n{stats.get('status', 'FAILED')}")
        
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="TARS CLI")
    subparsers = parser.add_subparsers(dest="command")

    knowledge_parser = subparsers.add_parser("knowledge")
    knowledge_subparsers = knowledge_parser.add_subparsers(dest="knowledge_command")

    import_parser = knowledge_subparsers.add_parser("import")
    import_parser.add_argument("file", help="Path to the JSON seed file")

    args = parser.parse_args()

    if args.command == "knowledge" and args.knowledge_command == "import":
        import_knowledge(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
