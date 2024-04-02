# main.py
from langchain.chat_models import ChatOpenAI
from src.search_recipes import pull_recipes, create_supabase_client
from src.utils import read_config, query_template
from src.run_chains import get_recipe_args, find_recipes
import os
import asyncio

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Set up the Supabase client
    #supabase_client = create_supabase_client()

    # Load configuration for API keys
    spoonacular_api_key = read_config()

    OPENAI_KEY =  os.getenv('OPENAI_API_KEY')

    # User query
    user_query = "I want a quick Italian dinner recipe that's vegetarian and includes garlic."
    #user_query = "I want a quick Italian dinner recipe that includes garlic."
    # OpenAI API key - Ensure this is securely stored, e.g., in environment variables or a config file
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")

    # Get recipe search arguments using OpenAI API
    cuisine, dietary_restrictions, meal_type, ingredients, recipe_type = get_recipe_args(user_query)

    # Pull recipes from Spoonacular API and save to Supabase
    db = pull_recipes(
        spoonacular_api_key,
        cuisine,
        dietary_restrictions,
        meal_type,
        ingredients,
        recipe_type,
        10  # Number of results you want
    )

    llm = ChatOpenAI(temperature=0, model="gpt-4-0613", openai_api_key=OPENAI_KEY)
    query = query_template(cuisine, meal_type, dietary_restrictions, ingredients, recipe_type)
    response = find_recipes(query, llm, db)

    print(f"Here's your suggested Recipe: : {response}")
