# Project README

## Overview

This project consists of multiple components designed to download website content, clean and process the HTML content into textual data, segment the cleaned data into manageable chunks, and finally vectorize the textual data for indexing into a vector database using Qdrant. It's an end-to-end pipeline from data acquisition to preparation for advanced search and retrieval capabilities.

### Components

1. **Web Downloader**: Uses `wget` to recursively download website content into a specified folder. This step focuses on acquiring the raw HTML, text, and temporary files necessary for further processing.

    ```
    wget -r -np -nd -A.html,.txt,.tmp -P websites {url}
    ```

2. **Cleaner (`cleaner.py`)**: A Python script that cleans and normalizes the downloaded HTML files, stripping them of HTML tags and other non-textual content, then saves the clean text to a new file.

3. **Chunkers (`chunker.py`, `htmlChunker.py`, `gptChunker.py`, `slidingChunker.py`)**: These scripts are various implementations for breaking down large text files into smaller, more manageable chunks. The methods vary from simple text splitting to more complex strategies involving HTML header tags and GPT-powered markdown conversion.

4. **Vectorizer (`vectorizer.py`)**: This script loads the processed text data, generates embeddings using OpenAI's models, and indexes these embeddings into a Qdrant vector database for efficient search and retrieval.

### Requirements

-  Dependencies listed in `requirements.txt`
  
  ```
  run pip install -r requirements.txt 
  ```

### Setup

1. **Install Dependencies**:
    - Ensure you have Python 3.x installed on your system.
    - Install the required Python packages by running `pip install -r requirements.txt`.

2. **Environment Variables**:
    - Create a `.env` file at the root of the project directory.
    - Add your OpenAI API key and any other required environment variables as specified in the scripts.

3. **Running the Project**:
    - Start by downloading the website content using the `wget` command.
    - Run the `cleaner.py` script to clean and normalize the downloaded content.
    - Choose a chunking strategy and run the corresponding script to segment the data.
    - Finally, run the `vectorizer.py` script to generate embeddings and index them into Qdrant.

### Usage

The scripts are designed to be run sequentially, starting from downloading the website content to indexing the processed data into Qdrant. Each script can be executed individually as per the requirements of the pipeline stage.

