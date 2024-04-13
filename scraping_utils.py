from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_extraction_chain
from bs4 import BeautifulSoup
import os
import pprint
from langchain_openai import ChatOpenAI



def main():
    urls = ["https://news.microsoft.com/ai/#top-ai-news"]
    schema = {
    "properties": {
        "news_article_title": {"type": "string"},
        "news_article_summary": {"type": "string"},
    },
    "required": ["news_article_title", "news_article_summary"],
    }

    extracted_content = scrape_with_playwright(urls, schema=schema)

def extract(content: str, schema: dict):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", api_key=openai_api_key)
    
    return create_extraction_chain(schema=schema, llm=llm).run(content)    

def scrape_with_playwright(urls, schema):
    loader = AsyncChromiumLoader(urls)
    docs = loader.load()
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        docs, tags_to_extract=["span"]
    )
    print("Extracting content with LLM")

    # Grab the first 1000 tokens of the site
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    splits = splitter.split_documents(docs_transformed)
    print(splits.count)
   

    # Process the first split
    extracted_content = extract(schema=schema, content=splits[0].page_content)
    pprint.pprint(extracted_content)
    return extracted_content




if __name__ == "__main__":
    main()   