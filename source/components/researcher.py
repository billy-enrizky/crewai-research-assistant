from typing import Type
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from exa_py import Exa
import requests
import streamlit as st
import os

class EXAAnswerToolSchema(BaseModel):
    query: str = Field(..., description="The question you want to ask Exa.")

class EXAAnswerTool(BaseTool):
    name: str = "Ask Exa a question"
    description: str = "A tool that asks Exa a question and returns the answer."
    args_schema: Type[BaseModel] = EXAAnswerToolSchema
    answer_url: str = "https://api.exa.ai/answer"
    
    def _run(self, query: str):
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": os.environ.get("EXA_API_KEY")
        }
        
        try:
            response = requests.post(
                self.answer_url,
                json={"query": query, "text": True},
                headers=headers,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Log the HTTP error
            print(f"Response content: {response.content}")  # Log the response content for more details
            raise
        except Exception as err:
            print(f"Other error occurred: {err}")  # Log any other errors
            raise
        
        response_data = response.json()
        answer = response_data["answer"]
        citations = response_data.get("citations", [])
        output = f"Answer: {answer}\n\n"
        if citations:
            output += "Citations:\n"
            for citation in citations:
                output += f"- {citation['title']} ({citation['url']})\n"

        return output            
    
#--------------------------------#
#         LLM & Research Agent   #
#--------------------------------#

def create_researcher(selection):
    """Create a research agent with the specified LLM configuration.
    
    Args:
        selection (dict): Contains provider and model information
            - provider (str): The LLM provider ("OpenAI", "GROQ", or "Ollama")
            - model (str): The model identifier or name
    
    Returns:
        Agent: A configured CrewAI agent ready for research tasks
    
    Note:
        Ollama models have limited function-calling capabilities. When using Ollama,
        the agent will rely more on its base knowledge and may not effectively use
        external tools like web search.
    """
    provider = selection["provider"]
    model = selection["model"]
    
    if provider == "GROQ":
        llm = LLM(
            api_key=os.environ.get("GROQ_API_KEY"),
            model=f"groq/{model}"
        )
        
    elif provider == "Ollama":
        llm = LLM(
            base_url="http://localhost:11434",
            model=f"ollama/{model}",
        )
        
    else:
        # Map friendly names to concrete model names for OpenAI
        if model == "GPT-3.5":
            model = "gpt-3.5-turbo"
        elif model == "GPT-4":
            model = "gpt-4"
        elif model == "o1":
            model = "o1"
        elif model == "o1-mini":
            model = "o1-mini"
        elif model == "o1-preview":
            model = "o1-preview"
        # If model is custom but empty, fallback
        if not model:
            model = "o1"
        llm = LLM(
            api_key=os.get.environ("OPENAI_API_KEY"),
            model=f"openai/{model}"
        )
    
    researcher = Agent(
        role='Research Analyst',
        goal='Conduct thorough research on given topics for the current year 2025',
        backstory='Expert at analyzing and summarizing complex information',
        tools=[EXAAnswerTool()],
        llm=llm,
        verbose=True,
        allow_delegation=False,  # Disable delegation to avoid caching
    )
    return researcher
    