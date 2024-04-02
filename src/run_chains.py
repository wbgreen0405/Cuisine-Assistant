import json
import os
import openai
import asyncio
#from openai import OpenAI
from langchain.tools import tool
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.llms.openai import OpenAI
from langchain.sql_database import SQLDatabase
from langchain.memory import ConversationBufferMemory
from sqlalchemy import create_engine
from supabase import create_client
import sys
sys.path.append('/content/drive/MyDrive/LLM/ChefAssist/src')
from functions_tools import recipe_agent_tools
from agent_constants import CUSTOM_SUFFIX


#from langchain_community.chat_models import OpenAI
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv

# Supabase and external API configurations


# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Set the OpenAI API key for authentication
openai.api_key = os.getenv('OPENAI_API_KEY')


supabase_url =  os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')


def get_recipe_args(user_query):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_for_recipes",
                "description": "Extracts information for a recipe search based on user's query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cuisine": {"type": "string", "description": "Type of cuisine."},
                        "dietary_restrictions": {"type": "string", "description": "Any dietary restrictions."},
                        "meal_type": {"type": "string", "description": "Type of meal."},
                        "ingredients": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ingredients."
                        },
                        "recipe_type": {"type": "string", "description": "Type of recipe, e.g., quick, healthy, traditional."}
                    },
                    "required": ["cuisine", "meal_type", "ingredients", "recipe_type"]
                }
            }
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": user_query}],
            tools=tools,
            temperature=0
        )
        
        # Parsing logic adjusted for the 'tool_calls' array structure
        tool_calls = response["choices"][0]["message"]["tool_calls"]
        if not tool_calls:
            raise ValueError("No 'tool_calls' found in the response.")
        
        # Assuming we're interested in the first tool call's function arguments
        function_call_arguments = tool_calls[0]["function"]["arguments"]
        
        # Now that we have the correct path, ensure JSON loading is necessary
        parsed_data = json.loads(function_call_arguments)
        
        return (
            parsed_data['cuisine'],
            parsed_data['dietary_restrictions'],
            parsed_data['meal_type'],
            parsed_data['ingredients'],
            parsed_data['recipe_type']
        )
    except Exception as e:
        print(f"Error during API call or processing response: {e}")
        return None, None, None, None, None



def find_recipes(query, llm, db):
    """
    Executes a search for recipes based on a natural language query.
    
    Parameters:
    - query (str): The natural language query to process.
    
    Returns:
    - The search results or an error message.
    """

    ## database connect string from env file
   
        # Retrieve database password from environment variables
    db_password = os.getenv('DB_password')
    
    # Correct the URI with the proper dialect and password
    #database_uri = f"postgres://postgres:{db_password}@postgres.dpoyobtpcwxvvfancngl.supabase.co:5432/postgres"
    database_uri = f"postgresql+psycopg2://postgres.dpoyobtpcwxvvfancngl:{db_password}@aws-0-us-west-1.pooler.supabase.com:5432/postgres"
    # Create an SQLAlchemy engine
    #engine = create_engine(database_uri)
    
    # Assuming SQLDatabase can be initialized with an SQLAlchemy engine
    db = SQLDatabase.from_uri(database_uri)
    agent_tools = recipe_agent_tools()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    memory = ConversationBufferMemory(memory_key="history", input_key="input")
  
    # Create the SQL agent using the adapter in place of a direct database connection
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,  # Your custom adapter for Supabase
        suffix=CUSTOM_SUFFIX,
        agent_executor_kwargs={"memory": memory},
        input_variables=["input", "agent_scratchpad", "history"],
        #input_variables=["input","history"],
        extra_tools=agent_tools,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )
    

    
    return agent_executor.run(query)



