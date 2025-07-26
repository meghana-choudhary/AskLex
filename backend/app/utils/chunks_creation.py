import time
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from app.llm.gemini_client import get_summary_chain
from app import config

embedding_model= config.EMBEDDING_MODEL_NAME
stitching_threshold= config.STITCHING_THRESHOLD
threshold_margin= config.THRESHOLD_MARGIN

splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " "]
)

def recursive_chunk_creation(full_text):

    if not full_text.strip():
        return []

    recursive_chunks = splitter.split_text(full_text)

    ordered_chunks = [
    {"chunk_id": f"chunk_{i+1}", "text": chunk}
    for i, chunk in enumerate(recursive_chunks)
    ]

    return ordered_chunks


def generate_chunk_summary_prompt(chunk_text):

    chain = get_summary_chain()
    result = chain.invoke({"chunk_text": chunk_text})
    return result

def generate_description_with_backoff(failed_chunks, max_retries=5, base_delay=60, extended_delay=150, max_delay=600):

    print("Generating Descriptions with Retry")
    for chunk in failed_chunks:
        retries = 0
        while True:
            try:
                summary = generate_chunk_summary_prompt(chunk["text"])
                if not isinstance(summary, dict) or "description" not in summary:
                    raise ValueError("Missing or malformed description in summary output.")
                description = summary.get("description", "").strip()

                if not description:
                    raise ValueError("Received empty or blank description from LLM.")

                chunk["description"] = description
                break

            except Exception as e:
                error_msg = str(e).lower()
                if "quota" in error_msg or "rate limit" in error_msg or "too many requests" in error_msg or "missing or malformed description" in error_msg or "empty or blank description" in error_msg:
                    retries += 1
                    if retries >= max_retries:
                        print(f"❗ Max retries hit for chunk {chunk.get('chunk_id')}. Sleeping {extended_delay}s and retrying again...")
                        time.sleep(extended_delay)
                        delay = extended_delay * (1.5 ** retries)
                        extended_delay = min(delay, max_delay)
                        retries = 0
                    else:
                        print(f"🔁 Retry {retries}/{max_retries} for chunk {chunk.get('chunk_id')}. Sleeping {base_delay}s...")
                        time.sleep(base_delay)
                else:
                    print(f"❌ Unrecoverable error on chunk {chunk.get('chunk_id', 'unknown')}: {e}")
                    chunk["description"] = None
                    break


def generate_chunk_descriptions_batched(ordered_chunks, batch_size=10, wait_time=65):
    """
    Process descriptions in batches of `batch_size` every `wait_time` seconds.
    """
    total_chunks = len(ordered_chunks)

    for i in tqdm(range(0, total_chunks, batch_size), desc="Generating Descriptions"):
        batch = ordered_chunks[i:i + batch_size]

        for chunk in batch:
            try:
                summary = generate_chunk_summary_prompt(chunk["text"])
                if not isinstance(summary, dict) or "description" not in summary:
                    raise ValueError("Missing or malformed 'description' in summary output.")
                chunk["description"] = summary["description"]
            except Exception as e:
                print(f"\n⚠️ Error in chunk {chunk.get('chunk_id', 'unknown')}: {e}")
                print(f"Text sample: {chunk['text'][:300]}...\n")
                chunk["description"] = None

        # Wait only if more chunks are left
        if i + batch_size < total_chunks:
            print(f"\n⏳ Waiting {wait_time} seconds to respect Gemini quota...")
            time.sleep(wait_time)

    failed_chunks = [
    c for c in ordered_chunks
    if c["description"] is None or not c["description"].strip()
    ]
    print(f"\nRetrying {len(failed_chunks)} failed chunks...")
    generate_description_with_backoff(failed_chunks)
    return ordered_chunks



def generate_embeddings(ordered_chunks, max_retries=3, retry_delay=30):
    valid_chunk_tuples = [(i, c) for i, c in enumerate(ordered_chunks) if c.get("description") and c["description"].strip()]
    descriptions = [c["description"] for _, c in valid_chunk_tuples]

    if not descriptions:
        print("🚫 No valid descriptions to embed.")
        return


    attempt = 0
    while attempt < max_retries:
        try:
            embeddings = embedding_model.embed_documents(descriptions)

            # Check for mismatch
            if len(embeddings) != len(valid_chunk_tuples):
                raise ValueError(
                    f"Mismatch: Got {len(embeddings)} embeddings for {len(valid_chunk_tuples)} valid descriptions"
                )

            break  # Successful embedding, exit retry loop

        except Exception as e:
            attempt += 1
            print(f"❌ Embedding attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print(f"🔁 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("🚫 Max retries exceeded. Falling back to None embeddings.")
                embeddings = [None] * len(descriptions)

    # Assign embeddings (even if they are None)
    for (i, _), emb in zip(valid_chunk_tuples, embeddings):
        ordered_chunks[i]["embedding"] = emb

    # Ensure all chunks have embedding key
    for i, chunk in enumerate(ordered_chunks):
        if "embedding" not in chunk:
            chunk["embedding"] = None

    return ordered_chunks


def chunks_stitching(ordered_chunks):

    stitched_chunks = []
    i = 0

    incomplete_chunks = [c for c in ordered_chunks if not c.get("description") or not c["description"].strip() or not c.get("embedding")]
    if incomplete_chunks:
        print(f"⚠️ Found {len(incomplete_chunks)} incomplete chunks — Filtering them out.")
        ordered_chunks = [
            c for c in ordered_chunks
            if c.get("description") and c["description"].strip() and c.get("embedding")
        ]
        
    while i < len(ordered_chunks):
        base_chunk = ordered_chunks[i]
        stitched_text = base_chunk["text"]
        stitched_description = base_chunk["description"]
        j = i + 1

        while j < len(ordered_chunks):
            base_embedding = np.array(base_chunk["embedding"])
            next_embedding = np.array(ordered_chunks[j]["embedding"])
            sim = cosine_similarity([base_embedding], [next_embedding])[0][0]

            if sim >= stitching_threshold - threshold_margin:
                stitched_text += "\n\n" + ordered_chunks[j]["text"]
                stitched_description += " + " + ordered_chunks[j]["description"]
                j += 1
            else:
                break

        stitched_chunks.append({
            "start_chunk_id": ordered_chunks[i]["chunk_id"],
            "end_chunk_id": ordered_chunks[j - 1]["chunk_id"],
            "text": stitched_text,
            "description": stitched_description
        })

        i = j 

    return stitched_chunks

if __name__ == "__main__":
    full_text= "Text to be chunked"
    ordered_chunks= recursive_chunk_creation(full_text)
    chunks_with_summary= generate_chunk_descriptions_batched(ordered_chunks)
    embedded_summary_chunks= generate_embeddings(chunks_with_summary)
    stitched_chunks= chunks_stitching(embedded_summary_chunks)
    print(stitched_chunks)






