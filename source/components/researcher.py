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
            api_key=os.environ.get("OPENAI_API_KEY"),
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

def create_research_task(researcher, task_description):
    """Create a research task for the agent to execute.
    
    Args:
        researcher (Agent): The research agent that will perform the task
        task_description (str): The research query or topic to investigate
    
    Returns:
        Task: A configured CrewAI task with expected output format
    """
    return Task(
        description=task_description,
        expected_output="""A comprehensive research report for the year 2025. 
        The report must be detailed yet concise, focusing on the most significant and impactful findings.
        
        Format the output in clean markdown (without code block markers or backticks) using the following structure:

        # Executive Summary
        - Brief overview of the research topic (2-3 sentences)
        - Key highlights and main conclusions
        - Significance of the findings

        # Key Findings
        - Major discoveries and developments
        - Market trends and industry impacts
        - Statistical data and metrics (when available)
        - Technological advancements
        - Challenges and opportunities

        # Analysis
        - Detailed examination of each key finding
        - Comparative analysis with previous developments
        - Industry expert opinions and insights
        - Market implications and business impact

        # Future Implications
        - Short-term impacts (next 6-12 months)
        - Long-term projections
        - Potential disruptions and innovations
        - Emerging trends to watch

        # Recommendations
        - Strategic suggestions for stakeholders
        - Action items and next steps
        - Risk mitigation strategies
        - Investment or focus areas

        # Citations
        - List all sources with titles and URLs
        - Include publication dates when available
        - Prioritize recent and authoritative sources
        - Format as: "[Title] (URL) - [Publication Date if available]"

        Note: Ensure all information is current and relevant to 2025. Include specific dates, 
        numbers, and metrics whenever possible to support findings. All claims should be properly 
        cited using the sources discovered during research.
        """,
        agent=researcher,
        output_file="output/research_report.md"
    )
    
#--------------------------------#
#         Research Crew          #
#--------------------------------#
def run_research(researcher, task):
    """Execute the research task using the configured agent.
    
    Args:
        researcher (Agent): The research agent to perform the task
        task (Task): The research task to execute
    
    Returns:
        str: The research results in markdown format
    """
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()