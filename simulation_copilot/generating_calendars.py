from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from simulation_copilot.resource_model import generate_calendar

# NOTE: TAVILY_API_KEY, OPENAI_ORGANIZATION_ID, OPENAI_API_KEY are required
#   to be set in the .env file or as environment variables
load_dotenv()


tavily_tool = TavilySearchResults()

tools = [tavily_tool, generate_calendar]

instructions = """You are an assistant who helps with business process simulation. 
You can help with generating a calendar for a resource."""
base_prompt = hub.pull("langchain-ai/openai-functions-template")
prompt = base_prompt.partial(instructions=instructions)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

print(
    agent_executor.invoke(
        {
            "input": "generate a calendar for a resource that works 8.30am to 7.30pm Monday to Wednesday, 11am to 9pm Thursday and Friday, and 9am to 5pm Saturday and Sunday."
        }
    )
)
