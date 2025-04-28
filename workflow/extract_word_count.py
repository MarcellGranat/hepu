from structure.paper import Paper, generate_papers
from tqdm import tqdm
from extract_epu.extract_epu import get_epu, PaperEPU
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
import os

class Batch(BaseModel):
    items: list[Paper]
    batch_number: int



def generate_batches(batch_size: int = 50):
    i = 0
    papers = []
    
    for paper in generate_papers():
        papers.append(paper)
        if len(papers) == batch_size:
            batch: Batch = Batch(items=papers, batch_number=i)
            i += 1
            papers = []
            yield batch

total_papers = len(list(generate_papers()))


if __name__ == "__main__":
    
    if not os.path.exists("data/epu_batches"):
        os.makedirs("data/epu_batches")

    with tqdm(total=total_papers, desc="Processing batches", colour="cyan") as pbar:
        for batch in generate_batches(batch_size=500):
            
            with ThreadPoolExecutor(max_workers=20) as executor:
                results = list(executor.map(get_epu, batch.items))

            with open(f"data/epu_batches/batch_{batch.batch_number}.jsonl", "w", encoding="utf-8") as file:
                for result in results:
                    file.write(result.model_dump_json() + "\n")
            
            pbar.update(len(batch.items))