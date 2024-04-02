import json
from datetime import datetime
from langchain.tools import Tool

# Assuming db is your database object from the `database.sql_db_langchain` module
#from database.sql_db_langchain import db

def run_query_save_results(db, query):
    """
    This function remains unchanged, reusing your approach to execute and parse queries.
    """
    res = db.run(query)
    res = [el for sub in ast.literal_eval(res) for el in sub]
    return res

def get_all_recipes(query: str) -> str:
    """
    Retrieves a list of all recipes.
    """
    query = "SELECT recipe_id, title, summary FROM recipe;"
    recipes = run_query_save_results(db, query)
    return json.dumps(recipes, ensure_ascii=False, indent=2)

def get_recipe_by_ingredient(query: str) -> str:
    """
    Fetches recipes based on a specific ingredient.
    """
    ingredient = query  # Assuming the query contains the ingredient name
    sql_query = f"""
    SELECT DISTINCT r.recipe_id, r.title, r.summary
    FROM recipe r
    JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
    JOIN ingredients i ON i.ingredient_id = ri.ingredient_id
    WHERE i.name ILIKE '%{ingredient}%';
    """
    recipes = run_query_save_results(db, sql_query)
    return json.dumps(recipes, ensure_ascii=False, indent=2)


def get_recipe_details(query: str) -> str:
    """
    Provides detailed information about a specific recipe.
    """
    recipe_id = query  # Assuming the query contains the recipe ID
    sql_query = f"""
    SELECT title, summary, directions, image_url, prep_time, cooking_time 
    FROM recipe 
    WHERE recipe_id = {recipe_id};
    """
    recipe_details = run_query_save_results(db, sql_query)
    return json.dumps(recipe_details, ensure_ascii=False, indent=2)


def recipe_agent_tools():
    tools = [
        Tool.from_function(
            func=get_all_recipes,
            name="get_all_recipes",
            description="Retrieves a list of all recipes.",
        ),
        Tool.from_function(
            func=get_recipe_by_ingredient,
            name="get_recipe_by_ingredient",
            description="Fetches recipes based on a specific ingredient.",
        ),
        Tool.from_function(
            func=get_recipe_details,
            name="get_recipe_details",
            description="Provides detailed information about a specific recipe.",
        ),
    ]
    return tools


