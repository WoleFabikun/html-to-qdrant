import os
from langchain.text_splitter import MarkdownHeaderTextSplitter
from tqdm.auto import tqdm
import hashlib
import json
import tiktoken
from textblob import TextBlob
from bs4 import BeautifulSoup
from openai import OpenAI

client = OpenAI()
tokenizer = tiktoken.get_encoding('cl100k_base')

def clean_html(html_content):
    try:
        print("Cleaning HTML content...")
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        cleaned_text = text.replace('\n', ' ').replace('\n\n', ' ')
        print("HTML content cleaned successfully.")
        return cleaned_text
    except Exception as e:
        print(f"Error cleaning HTML: {e}")
        return ""
    
def tiktoken_len(text):
    try:
        print("Calculating token length...")
        tokens = tokenizer.encode(text, disallowed_special=())
        print(f"Token length: {len(tokens)}")
        return len(tokens)
    except Exception as e:
        print(f"Error calculating token length: {e}")
        return 0

def split_text_in_half(text, max_tokens=3900):
    try:
        print("Splitting text into halves...")
        if tiktoken_len(text) <= max_tokens:
            print("Text length is within the maximum token limit.")
            return [text]

        chunks = []
        current_chunk = ""
        words = text.split()
        for word in words:
            if tiktoken_len(current_chunk + " " + word) <= max_tokens // 2:
                current_chunk += " " + word
            else:
                chunks.append(current_chunk.strip())
                current_chunk = word
        if current_chunk:
            chunks.append(current_chunk.strip())

        if len(chunks) == 1:
            return chunks

        result = []
        for chunk in chunks:
            result.extend(split_text_in_half(chunk, max_tokens))
        print(f"Text split into {len(result)} chunks.")
        return result
    except Exception as e:
        print(f"Error splitting text: {e}")
        return []

def gpt_convert_to_markdown(html_content):
    try:
        print("Converting HTML content to Markdown...")
        chunks = split_text_in_half(html_content)
        markdown_content = ""
        for chunk in chunks:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"""
    Given the cleaned HTML text below, please carefully analyze and extract the most crucial information, facts, and contextual details. As much as possible. Format your response in Markdown, using headers for categorization and bullet points or numbered lists to detail key points and facts. The goal is to transform the text into a structured, informative, detailed and context-rich Markdown document that serves as an ideal input for a Q&A vector database, focusing on accuracy, detail, and relevance for semantic search capabilities. It is crucial that the markdown that you give is rich with detail so that when the vectors with the relevant information is searched for it is easy and accurate. Give precedencence to the most updated information for this year. 
    ---
    {chunk}
    ---
    Markdown:
    """},
                ]
            )
            markdown_content += response.choices[0].message.content
        print("Conversion to Markdown completed.")
        return markdown_content.strip()
    except Exception as e:
        print(f"Error converting to Markdown: {e}")
        return ""

def process_html_files(folder_path):
    try:
        print(f"Processing HTML files in folder: {folder_path}")
        all_files = os.listdir(folder_path)
        html_files = [file for file in all_files if file.endswith('.txt')]
        print(f"Found {len(html_files)} HTML files.")

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=True)

        documents = []

        for html_file in tqdm(html_files):
            try:
                file_path = os.path.join(folder_path, html_file)
                print(f"Processing file: {file_path}")
                with open(file_path, 'r') as f:
                    content = f.read()

                cleaned_content = clean_html(content)
                if not cleaned_content:
                    raise Exception("Failed to clean HTML content")

                markdown_content = gpt_convert_to_markdown(cleaned_content)
                if not markdown_content:
                    raise Exception("Failed to convert to Markdown")

                markdown_splits = markdown_splitter.split_text(markdown_content)

                for i, split in enumerate(markdown_splits):
                    blob = TextBlob(split.page_content)
                    noun_phrases = blob.noun_phrases
                    unique_noun_phrases = list(set(noun_phrases))

                    topics = [value for key, value in split.metadata.items() if key.startswith('Header')]
                    for key in list(split.metadata.keys()):
                        if key.startswith('Header'):
                            del split.metadata[key]
                    split.metadata['topics'] = topics
                    split.metadata['keywords'] = unique_noun_phrases

                    documents.append({
                        'id': f"{hashlib.md5(file_path.encode('utf-8')).hexdigest()[:12]}-{i}",
                        'text': split.page_content,
                        'metadata': split.metadata
                    })

                print(f"File {html_file} processed successfully.")
            except Exception as e:
                print(f"Error processing file {html_file}: {e}")

        if not documents:
            raise Exception("No documents were generated")

        with open('train.jsonl', 'w') as f:
            for doc in documents:
                f.write(json.dumps(doc) + '\n')

        print("All documents processed and saved successfully.")
        return documents
    except Exception as e:
        print(f"Error processing HTML files: {e}")
        return []  

folder_path = "websites"  
documents = process_html_files(folder_path)
