import os
from langchain.document_loaders import ReadTheDocsLoader
from tqdm.auto import tqdm
import hashlib
import json
import tiktoken
from textblob import TextBlob
from bs4 import BeautifulSoup

tokenizer = tiktoken.get_encoding('cl100k_base')

def clean_html(html_content):
    # Use Beautiful Soup to remove HTML tags
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    # Replace newline characters with a space
    cleaned_text = text.replace('\n', ' ')
    cleaned_text = cleaned_text.replace('\n\n', ' ')
    return cleaned_text

def tiktoken_len(text):
    tokens = tokenizer.encode(
        text, disallowed_special=()
    )
    return len(tokens)

def split_into_sentences(text):
    blob = TextBlob(text)
    return [str(sentence) for sentence in blob.sentences]

def hybrid_chunking(text, min_chunk_size, max_chunk_size, window_size, step_size):
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = []
    current_chunk_size = 0

    for sentence in sentences:
        sentence_tokens = tokenizer.encode(sentence, disallowed_special=())
        sentence_size = len(sentence_tokens)

        if current_chunk_size + sentence_size <= max_chunk_size:
            current_chunk.append(sentence)
            current_chunk_size += sentence_size
        else:
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                blob = TextBlob(chunk_text)
                keywords = list(set(blob.noun_phrases))
                chunks.append({
                    'text': chunk_text,
                    'chunk_id': len(chunks),
                    'keywords': keywords
                })
            current_chunk = [sentence]
            current_chunk_size = sentence_size

    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        blob = TextBlob(chunk_text)
        keywords = list(set(blob.noun_phrases))
        chunks.append({
            'text': chunk_text,
            'chunk_id': len(chunks),
            'keywords': keywords
        })

    sliding_chunks = []
    for chunk in chunks:
        chunk_text = chunk['text']
        chunk_tokens = tokenizer.encode(chunk_text, disallowed_special=())
        chunk_size = len(chunk_tokens)

        if chunk_size <= window_size:
            sliding_chunks.append(chunk)
        else:
            for i in range(0, chunk_size - window_size + 1, step_size):
                window_text = tokenizer.decode(chunk_tokens[i:i + window_size])
                blob = TextBlob(window_text)
                keywords = list(set(blob.noun_phrases))
                sliding_chunks.append({
                    'text': window_text,
                    'chunk_id': len(sliding_chunks),
                    'keywords': keywords
                })

    return sliding_chunks

def process_txt_files(folder_path, min_chunk_size, max_chunk_size, window_size, step_size):
    # Get all files in the folder
    all_files = os.listdir(folder_path)
    # Filter out HTML files
    txt_files = [file for file in all_files if file.endswith('.txt')]

    documents = []

    # Process each HTML file
    for txt_file in tqdm(txt_files):
        try:
            file_path = os.path.join(folder_path, txt_file)
            with open(file_path, 'r') as f:
                content = f.read()
            # Generate a unique ID based on the file path
            m = hashlib.md5()
            m.update(file_path.encode('utf-8'))
            uid = m.hexdigest()[:12]
            # Clean the HTML content
            cleaned_content = clean_html(content)
            # Split the content into chunks
            chunks = hybrid_chunking(cleaned_content, min_chunk_size, max_chunk_size, window_size, step_size)
            # Create document data
            for chunk in chunks:
                documents.append({
                    'id': f"{uid}-{chunk['chunk_id']}",
                    'text': chunk['text'],
                    'keywords': chunk['keywords'],
                })
            # Delete the HTML file after processing
            os.remove(file_path)
        except Exception as e:
            print(f"Error processing file {txt_file}: {e}")

    # Save the documents to a JSONL file
    with open('train.jsonl', 'w') as f:
        for doc in documents:
            f.write(json.dumps(doc) + '\n')

    return documents

# Call the function with the folder path "websites"
folder_path = "websites"
min_chunk_size = 100  # Adjust the minimum chunk size as needed
max_chunk_size = 200  # Adjust the maximum chunk size as needed
window_size = 150  # Adjust the sliding window size as needed
step_size = 50  # Adjust the sliding window step size as needed
documents = process_txt_files(folder_path, min_chunk_size, max_chunk_size, window_size, step_size)