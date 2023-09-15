from typing import List
from pathlib import Path

from langchain.schema import Document
from data_integration_questionnaire.config import cfg
from data_integration_questionnaire.log_init import logger
from data_integration_questionnaire.service.embedding_service import (
    generate_embeddings,
    load_text,
)

from langchain.vectorstores import FAISS


def init_vector_search() -> FAISS:
    embedding_dir = cfg.embeddings_persistence_dir.as_posix()
    embedding_dir_path = Path(embedding_dir)
    if embedding_dir_path.exists() and len(list(embedding_dir_path.glob("*"))) > 0:
        logger.info(f"reading from existing directory")
        docsearch = FAISS.load_local(embedding_dir, cfg.embeddings)
        return docsearch
    else:
        logger.warning(f"Cannot find path {embedding_dir} or path is empty.")
        doc_location = cfg.raw_text_folder
        logger.info(f"Using doc location {doc_location}.")
        logger.info("Generating vectors")
        documents = load_text(doc_location=doc_location)
        docsearch = generate_embeddings(
            documents=documents, persist_directory=embedding_dir
        )
        return docsearch
    

def similarity_search(docsearch: FAISS, input: str) -> str:
    how_many = cfg.search_results_how_many
    doc_list = docsearch.similarity_search(input, k=how_many)
    return "\n\n".join([p.page_content for p in doc_list])
    

if __name__ == "__main__":
    docsearch = init_vector_search()
    search_res = similarity_search(docsearch, "Data Quality")
    print(search_res)

