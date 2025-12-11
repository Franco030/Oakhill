import json
import os

class NoteManager:
    def __init__(self, base_path, language="en"):
        self.base_path = base_path
        self.current_language = language
        self.notes_data = {}
        
        self.load_database()

    def load_database(self):
        path = os.path.join(self.base_path, "data/notes.json")
        
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.notes_data = json.load(f)
            except Exception as e:
                print(f"[NoteManager] Error loading JSON: {e}")
        else:
            print(f"[NoteManager] ERROR: {path} not found")

    def set_language(self, lang_code):
        self.current_language = lang_code

    def get_note_content(self, note_id):
        raw_data = self.notes_data.get(note_id)
        
        if not raw_data:
            return None

        contents = raw_data.get("content", {})
        raw_text = contents.get(self.current_language, contents.get("en", ""))

        pages = raw_text.split("[P]")
        clean_pages = [p.strip() for p in pages if p.strip()]

        return {
            "id": note_id,
            "pages": clean_pages,
            "total_pages": len(clean_pages)
        }