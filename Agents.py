import os
import autogen

from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_extraction_chain
from bs4 import BeautifulSoup
import os
import pprint
from langchain_openai import ChatOpenAI
from scraping_utils import extract, scrape_with_playwright

class Agents:
    def __init__(self, config_list, llm_config, user_proxy: autogen.UserProxyAgent,assistant:autogen.AssistantAgent,):
        # Define configuration list for autogen models
        self.config_list = config_list

        # Configure settings for the autogen language model
        self.llm_config = llm_config
        self.assistant = assistant
        self.user_proxy = user_proxy        
#
def main():

    # Initialize the agents
    config_list = [
    {
        'model': 'gpt-4',
        'api_key': os.getenv("OPENAI_API_KEY")
    }
    ]

    # Configure settings for the autogen language model
    llm_config = {
        "seed": 42,  # Setting a seed for reproducibility
        "config_list": config_list,
        "temperature": 0  # Disabling randomness in generation
    }
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "/home/albert/Documents/work_dir"
                               ,"use_docker":False},
        
        llm_config=llm_config,
        system_message="""
        Reply TERMINATE if the task has been solved to full satisfaction. 
        Otherwise, reply CONTINUE, or provide a reason why the task is not yet solved."""
    )

    # Initialize assistant agent
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config=llm_config,
        system_message="You should generate code and store it in a file as mentioned in the {code_execution_config}"
    )
    agents = Agents(user_proxy=user_proxy, assistant=assistant, config_list=config_list, llm_config=llm_config)

    # AI Topic Generation task
    
    urls = ["https://news.microsoft.com/ai/#top-ai-news"]
    schema = {
    "properties": {
        "news_article_title": {"type": "string"},
        "news_article_summary": {"type": "string"},
    },
    "required": ["news_article_title", "news_article_summary"],
    }

    extracted_content = scrape_with_playwright(urls, schema=schema)
    print(extracted_content)

    # AI Resource genration task
    task= """
    Read  the variable{extracted_content} and write it to a file.
    """

    # # AI Resource genration task
    # task = """
    # Print out the list in the file high_level_topics.txt.
    # """

    # Initiate chat with the assistant
    agents.user_proxy.initiate_chat(
        agents.assistant,
        message=task,
    )


if __name__ == "__main__":
    main()          
  


 