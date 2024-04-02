import supabase
from supabase import create_client, Client
import requests
import json
import os
from dotenv import load_dotenv


# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Supabase and external API configurations
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API')
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')

def create_supabase_client():
    """
    Create a Supabase client using the URL and Key from environment variables.
    """
    #load_dotenv()  # Load environment variables from .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    SUPABASE_URL = os.getenv('SUPABASE_URL')  # Get Supabase URL from environment variable
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # Corrected to use the right environment variable
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception("Supabase URL or Key is not set in environment variables.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)



supabase = create_supabase_client()  # Create the Supabase client


def fetch_recipe_details(api_key, recipe_id):
    """
    Fetch detailed information for a recipe by ID.

    Parameters:
    - api_key (str): Spoonacular API key.
    - recipe_id (int): The ID of the recipe to fetch details for.
    
    Returns:
    - A dictionary containing detailed recipe information, including the sourceUrl.
    """
    details_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {
        'apiKey': api_key,
    }
    response = requests.get(details_url, params=params)
    if response.status_code == 200:
        return response.json()  # This includes detailed info, such as `sourceUrl`.
    else:
        print(f"Failed to retrieve recipe details. Status code: {response.status_code}, Response: {response.text}")
        return None


def save_recipes_to_supabase(recipes_data):
    """
    Saves the fetched recipes data into the Supabase database.
    Assumes that 'recipes' and 'ingredients' tables exist.
    """
    for recipe in recipes_data.get('results', []):
        recipe_data = {
            "title": recipe.get("title", "No Title Provided"),
            "summary": recipe.get("summary", "No Summary Provided"),
            "directions": recipe.get("instructions", "No Instructions Provided"),
            "image_url": recipe.get("image", ""),
            "prep_time": recipe.get("readyInMinutes", 0),
            "cooking_time": recipe.get("cookingMinutes", 0),
            "cuisine_type": ", ".join(recipe.get("cuisines", [])) if recipe.get("cuisines") else "Not Specified",
            "meal_type": ", ".join(recipe.get("dishTypes", [])) if recipe.get("dishTypes") else "Not Specified",
            "dietary_restrictions": ", ".join(recipe.get("diets", [])) if recipe.get("diets") else "Not Specified",
            "spoonacular_source_url": recipe.get("sourceUrl", ""),
            "recipe_type": recipe.get("type", "Not Specified")  # Add the new field here
        }

        # Insert or update the recipe in the 'recipes' table and capture the inserted recipe's ID
        inserted_recipe = supabase.table("recipe").insert(recipe_data).execute()
        recipe_id = inserted_recipe.data[0]["recipe_id"]

        # Iterate over the ingredients in the recipe
        for ingredient in recipe.get('extendedIngredients', []):
            # Check if this ingredient already exists in the 'ingredients' table
            existing_ingredient = supabase.table("ingredients").select("ingredient_id").eq("name", ingredient["name"]).execute()
            ingredient_id = None
            if existing_ingredient.data:
                ingredient_id = existing_ingredient.data[0]["ingredient_id"]
            else:
                # If it doesn't exist, insert it into the 'ingredients' table
                inserted_ingredient = supabase.table("ingredients").upsert({"name": ingredient["name"]}).execute()
                ingredient_id = inserted_ingredient.data[0]["ingredient_id"]

            # Check if the recipe-ingredient association already exists
            existing_association = supabase.table("recipe_ingredients").select("*").eq("recipe_id", recipe_id).eq("ingredient_id", ingredient_id).execute()
            if not existing_association.data:
                # Insert a record into the 'recipe_ingredients' table associating the recipe with this ingredient
                supabase.table("recipe_ingredients").insert({
                    "recipe_id": recipe_id,
                    "ingredient_id": ingredient_id,
                    "quantity": ingredient["amount"]  # Adjust as needed based on your schema
                }).execute()


def pull_recipes(api_key, cuisine, dietary_restrictions, meal_type, ingredients, recipe_type, number_of_results=10):
    """
    Pulls recipes from Spoonacular API and saves them to Supabase.
    """
    params = {
        'apiKey': api_key,
        'cuisine': cuisine,
        'diet': dietary_restrictions,
        'type': meal_type,
        'includeIngredients': ','.join(ingredients),
        'number': number_of_results,
        'instructionsRequired': True,
        'addRecipeInformation': True,
        'fillIngredients': True
    }
    response = requests.get('https://api.spoonacular.com/recipes/complexSearch', params=params)
    recipes_data = response.json()
    save_recipes_to_supabase(recipes_data)
