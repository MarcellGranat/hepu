from pydantic import BaseModel, computed_field
from json import load
from structure.paper import Paper
import re

with open("data/glossaries.json", "r", encoding="utf-8") as file:
    glossaries_dict = load(file)

def get_glossaries() -> dict:
    """Returns the glossary words."""
    global glossaries_dict
    return glossaries_dict

def set_glossaries(glossaries: dict) -> None:
    """Sets the glossary words."""
    global glossaries_dict
    glossaries_dict = glossaries

class PaperEPU(Paper):
    @computed_field
    @property
    def epu(self) -> dict:
        """Returns the EPU words."""
        global glossaries_dict
        word_counts = {key: [] for key in glossaries_dict.keys()}
        total_counts = {key: 0 for key in glossaries_dict.keys()}
        
        text_lower = self.text.lower()
        
        for category, words in glossaries_dict.items():
            matched_words: list[str] = [word for word in words if re.search(fr"\b{word}", text_lower)]
            word_counts[category] = ", ".join(matched_words)
            total_counts[category] = sum(len(re.findall(fr"\b{word}", text_lower)) for word in words)
        
        return {"word_counts": word_counts, "total_counts": total_counts}
    
def get_epu(paper: Paper) -> PaperEPU:
    """Returns the EPU words."""
    return PaperEPU(**paper.model_dump())

if __name__ == "__main__":
    from structure.paper import generate_papers
    for paper in generate_papers():
        paperepu = get_epu(paper)
        print(paperepu.epu)

        print(paperepu.model_dump_json())
        break
