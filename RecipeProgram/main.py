from flask import Flask, request, jsonify
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import json

app = Flask(__name__)

df_ingredients = pd.read_csv('ingredients.csv', names=['id',"materialName"],header=0)
df_recipe = pd.read_csv('Yemek.csv', names=['recipeID','recipeName','recipeType','recipeMaterialId','recipeMaterial','recipeCount','recipePrepartion','recipeCooking','recipeDescription'], header=0)
df_recipe['Malzemeler'] = df_recipe['recipeMaterial'].apply(lambda x: ast.literal_eval(x))
df_recipe['MalzemelerId'] = df_recipe['recipeMaterialId'].apply(lambda  x:ast.literal_eval(x))
mlb = MultiLabelBinarizer()
encoded_ingredients =mlb.fit_transform(df_recipe['MalzemelerId'])
encoded_df = pd.DataFrame(encoded_ingredients, columns=mlb.classes_)

#def get_recipeEntity(id):
#   recipeId= df_recipe.loc[df_recipe['recipeID']==id, 'recipeName', 'recipeType','recipeMaterial','recipeCount','recipePrepartion','recipeCooking','recipeDescription']
# return recipeId

def get_recipeEntity(id):
    recipe = df_recipe.loc[df_recipe['recipeID']==id].copy()
    recipe['recipeMaterial'] = recipe['recipeMaterial'].apply(ast.literal_eval)
    del recipe['recipeMaterialId']
    del recipe['Malzemeler']
    del recipe['MalzemelerId']
    return recipe.iloc[0].to_dict()

def get_materialId(material):
    user_ingredients =[]
    for material_name in material:
        material_id = df_ingredients.loc[df_ingredients['materialName'] == material_name, 'id'].values[0]
        user_ingredients.append(str(material_id))
    return user_ingredients

def get_best_recipes_with_scores(user_ingredients, encoded_df, df_recipe, mlb, top_n=15):
    encoded_user_ingredients = mlb.transform([user_ingredients])
    similarity_scores = cosine_similarity(encoded_user_ingredients, encoded_df.values)
    sorted_similarity_indices = similarity_scores.argsort()[0][::-1]
    top_recipe_indices = sorted_similarity_indices[:top_n]
    top_scores = similarity_scores[0][top_recipe_indices]
    top_recipes = df_recipe.iloc[top_recipe_indices].copy()
    top_recipes.loc[:, 'score'] = top_scores
    return top_recipes

@app.route('/get_recipes', methods=['POST'])
def get_recipes():
    data = request.get_json(force=True)
    print(data)
    user_ingredients = get_materialId(data['ingredients'])
    best_recipes = get_best_recipes_with_scores(user_ingredients, encoded_df, df_recipe, mlb, top_n=15)
    result = best_recipes.to_dict(orient='records')
    RecipeList =[]
    for recipe in result:
        del recipe['recipeMaterialId']
        del recipe['Malzemeler']
        del recipe['MalzemelerId']
        recipe['recipeMaterial'] = json.loads(recipe['recipeMaterial'].replace("'", "\""))
        RecipeList.append(recipe)
    print(RecipeList)
    return jsonify(RecipeList)


@app.route('/get_recipe/<int:recipeId>', methods=['GET'])
def get_recipe(recipeId):
    getRecipe=get_recipeEntity(recipeId)
    print(getRecipe)
    return jsonify(getRecipe)
if __name__ == '__main__':
    app.run(port = 5000)