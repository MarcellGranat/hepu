from pydantic import BaseModel
import os
import re
from pregex.core.classes import AnyLetter, AnyDigit, AnyFrom
from pregex.core.quantifiers import Optional, AtLeastAtMost
from pregex.core.operators import Either
from pregex.core import Pregex
import yaml
import fitz

date_pattern = Either("18", "19", "20") + AnyDigit() * 2 + "-" + AnyDigit() * 2 + "-" + AnyDigit() * 2

file_number_pattern = "-" + AtLeastAtMost(AnyDigit(), n = 1, m = 2) + ".pdf"

paper_pattern = Either(
    "nepszava",
    "pesti_hirlap",
    "nepakarat",
    "nepszabadsag",
    "szabad_nep"
    )

class Paper(BaseModel):
    # """Model representing a paper with its attributes."""
    basename: str
    paper: str
    date: str
    files: list[str]

    @property
    def text(self) -> str:
        """Extract text from the first PDF file."""
        
        text = ""
        for  file in self.files:
            pdf_path = file
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text("text") + "\n"
        return text

def subfolders_in_folder(folder_path: str | None = None):
    """Generator to yield subfolders in a given folder."""
    if not folder_path:
        with open("configs/config.yaml", "r") as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

        path: str = config["data_folder"]

    else:
        path = folder_path

    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            yield os.path.join(root, dir_name)

def papers_in_subfolder(subfolder_path: str) -> list[Paper]:
    papers = []
    for root, dirs, files in os.walk(subfolder_path):
        for file in files:
            if file.endswith(".pdf"):
                for file_name in files:
                    if file_name.endswith(".pdf"):
                        if file_name.endswith("header-1.pdf"):
                            continue

                        if Pregex("bioritmus_melleklet").has_match(file_name):
                            continue

                        basename = re.sub(r"-\d+\.pdf$", "", os.path.join(root, file_name))
                        file_path = os.path.join(root, file_name)
                        if basename not in [p.basename for p in papers]:
                            try:
                                paper = Paper(
                                    basename=basename,
                                    paper=paper_pattern.get_matches(basename)[0],
                                    date=date_pattern.get_matches(basename)[0],
                                    files=[file_path]
                                )
                            except Exception as e:
                                continue

                            papers.append(paper)

                        else:
                            for paper in papers:
                                if paper.basename != basename:
                                    continue

                                if file_path not in paper.files:
                                    paper.files.append(file_path)

    return papers
                    
def generate_papers(folder_path: str | None = None):
    """Get all papers in a folder."""
    for subfolder in subfolders_in_folder(folder_path):
        papers = papers_in_subfolder(subfolder)
        for paper in papers:
            yield paper

if __name__ == "__main__":
    folder_path = "E:/projects/arcanum-pw/data"  # Replace with your folder path
    subfolders = subfolders_in_folder()
    for subfolder in subfolders:
        papers = papers_in_subfolder(subfolder)
        for paper in papers:
            print(f"Paper: {paper.paper}, Date: {paper.date}, Edition: {paper.edition}, Files: {paper.files} ")
        break