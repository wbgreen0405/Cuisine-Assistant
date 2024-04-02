import yaml
import os

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def read_config():
    """
    Fetches API keys from environment variables.

    This function directly reads the Spoonacular API key from the environment variables,
    which should be set in the .env file or the execution environment.

    Returns:
    str: The API key for the Spoonacular API.
    """
    return os.getenv('SPOONACULAR_API_KEY')


def query_template(cuisine, meal_type, dietary_restrictions, ingredients, recipe_type):
    """
    Generates a formatted query string for recipe search based on user criteria.

    This function takes user criteria about recipes and formats it into a string that specifies the 
    required structure of the response. The structure includes details about the recipe like title, 
    summary, ingredients, directions, and nutritional information.

    Parameters:
    cuisine (str): The type of cuisine.
    meal_type (str): The type of meal (e.g., breakfast, lunch, dinner).
    dietary_restrictions (str): Any dietary restrictions (e.g., vegetarian, gluten-free).
    ingredients (list): A list of ingredients the user wants to include.
    recipe_type (str): Characteristics of the recipe (e.g., quick, healthy).

    Returns:
    query (str): A formatted string describing the required structure of the response.
    """

    query_template = f'''Find me a recipe that matches the following criteria:
- Cuisine type: "{cuisine}"
- Meal type: "{meal_type}"
- Dietary restrictions: "{dietary_restrictions}"
- Must include the following ingredients: {', '.join([f'"{ingredient}"' for ingredient in ingredients])}
- Recipe characteristics: "{meal_type}"

Respond with the recipe information in the following structure:
## Recipe ID: 
### Title: 
**Summary:**
- Cuisine: 
- Meal type: 
- Dietary restrictions: 
**Ingredients:**
- {', '.join([f"{ingredient}" for ingredient in ingredients])}
**Directions:**
- Step 1: 
- Step 2: 
- (Continue with additional steps as needed)
**Image URL:**
- (If available)
**Spooncular Source URL**
-(if available)
**Nutritional Information:**
- Calories:
- Carbohydrates (g):
- Protein (g):
- Fat (g):
(Include any other nutritional information if available)
'''
    return query_template