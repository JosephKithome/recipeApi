from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


import tempfile
import os
from PIL import Image


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


RECIPE_URL = reverse("recipe:recipe-list")

def detail_url(recipe_id):
    """Return reciperecipe_id detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])



def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults ={
        'title':'sample recipe',
        'time_minutes':10,
        'price':5.00
    }

    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)

def sample_tag(user, name="Sample Tag"):
    """Creates and returns a sample tag"""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name="Sample Ingredient"):
    """Creates and returns a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


class PublicApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client =APIClient()

        def test_auth_required(self):
            """Test that authentication is required"""
            res = self.client.get(RECIPE_URL)

            self.assertEqual(res.status_code, status.HTTP_400_UNAUTHORIZED)
            

class PrivateRecipeApiTest(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user =get_user_model().objects.create_user(
            'test@joseph.com',
            'testPASS'
        )

        # authenticating the user
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""

        user2 = get_user_model().objects.create_user(
            "other@gmail.com",
            "testOPASSS"
        )

        # creates two recipes with different users
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user) # filter with user
        serializer = RecipeSerializer(recipes, many=True)
        
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data, serializer.data)

    
    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""

        recipe =sample_recipe(user=self.user)
        recipe.tag.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)


    def test_create_basic_recipe(self):
        """Test creating recipe"""

        payload ={
            'title':'ugali sukuma',
            'time_minutes':30,
            'price':5.00,   
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe =Recipe.objects.get(id=res.data['id'])

        #Loop
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        


        def test_create_recipe_with_tags(self):
            """Test creating a recipe with tags """
            tag1 =sample_tag(user=self.user, name="vegan")
            tag2 = sample_tag(user=self.user, name="Dessert")

            payload ={
                "title":"Avocado lime cheesecake",
                'tag':[
                    tag1.id,
                    tag2.id
                ],
                'time_minutes': 60,
                'price': 20.00
            }
            # creates a recipe"""
            res = self.client.post(RECIPE_URL, payload)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)

            # retrieve the recipe that was created"""
            recipe = Recipe.objects.get(id=res.data['id'])
            tags = recipe.tags.all()

            self.assertEqual(tags.count(), 2)
            self.assertIn(tag1, tags) #check if tag is present in tags retrieved
            self.assertIn(tag2, tags)

        def test_create_recipe_with_ingredients(self):
            """Test creating recipe with ingredients """

            ingredient1 = sample_ingredient(user=self.user, name="Garlic")
            ingredient2 = sample_ingredient(user=self.user, name="Garlitos")

            payload ={
                "title": "The garlic",
                "ingredients":[ingredient1, ingredient2],
                "time_minutes":20,
                "price":25.00
            }

            res = self.client.post(RECIPE_URL, payload)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            
            recipe = Recipe.objects.get(res.data['id'])
            ingredients = recipe.ingredients.all()

            self.assertEqual(ingredients.count(), 2)
            self.assertIn(ingredient1, ingredients)
            self.assertIn(ingredient2, ingredients)


        def test_partial_update_recipe(self):
            """Test updating a recipe with patch"""
            recipe = sample_recipe(user=self.user)
            recipe.tag.add(sample_tag(user=self.user))
            new_tag=sample_tag(user=self.user, name ="New tag name")

            payload = {
                'title':"Chicken tikka",
                "tag":[new_tag.id]
            }  

            url = detail_url(recipe.id)
            self.client.patch(url,payload) # Making the request

            recipe.refresh_from_db() 

            self.assertEqual(recipe.title, payload['title'])

            tags=recipe.tag.all()

            self.assertEqual(len(tag), 1)
            self.assertIn(new_tag, tags)

        def test_full_update_recipe(self):
            """Test updating recipe with put"""

            recipe = sample_recipe(user=self.user)
            recipe.tag.add(sample_tag(user=self.request.user))

            payload={
                'title': "Spaghetti carbonara",
                'time_minutes': 25,
                'price':5.00,

            } 

            url = detail_url(recipe.id)
            self.client.put(url, payload)

            recipe.refresh_from_db()

            self.assertEqual(recipe.title, payload['title'])
            self.assertEqual(recipe.time_minutes, payload['time_minutes']) 
            self.assertEqual(recipe.price, payload['recipe'])

            tags = recipe.tag.all()
            self.assertEqual(len(tags), 0)



class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user =get_user_model().objects.create_user("user@softwadev.com","testPASS")
        self.client.force_authenticate(self.user)
        self.recipe =sample_recipe(user=self.user)
        
    def tearDown(self):
        self.recipe.image.delete()


    # def test_upload_image_to_recipe(self):
    #     """Test uploading an image to recipe"""

    #     url = image_upload_url(self.recipe.id)

    #     with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf: 
    #         img = Image.new('RGB', (10, 10))
    #         img.save(ntf, format='JPEG')
    #         ntf.seek(0)  
    #         res = self.client.post(url, {'image': ntf}, format='multipart')

    #     self.recipe.refresh_from_db()
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertIn('image', res.data)
    #     self.assertTrue(os.path.exists(self.recipe.image.path))


        def test_upload_image_bad_request(self):
            """Test uploading invalid image"""
            res = self.client.post(url,{'image':"notimage"}, format="multipart")

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        def test_filter_recipes_by_tags(self):
            """Test returning recipes with specific tags"""
            recipe1 = sample_recipe(user=self.user, title="The vegetable curry")
            recipe2 = sample_recipe(user=self.user, title="Recipe 2")

            tag1 = sample_tag(user=self.user, name="Tag 1")
            tag2 = sample_tag(user=self.user, name="Tag 2")

            recipe1.tag.add(tag1)
            recipe2.tag.add(tag2)

            recipe3 = sample_recipe(user=self.user, title="Fishh and chips")


            res = self.client.get(RECIPE_URL,{'tag':f'{tag1.id, tag2.id}'})
            serializer1 = RecipeSerializer(recipe1)
            serializer2 = RecipeSerializer(recipe2)
            serializer3 = RecipeSerializer(recipe3)

            self.assertIn(serializer1.data, res.data)
            self.assertIn(serializer2.data, res.data)
            self.assertNotIn(serializer3.data, res.data)

        def test_filter_recipes_by_ingredients(self):
            """Test returning recipes with specific ingredients"""
            recipe1 = sample_recipe(user=self.user, title="Posh beans on toast")
            recipe2 = sample_recipe(user=self.user, title="GArlic on toast")
            recipe3 = sample_recipe(user=self.user, title="Mango butter")

            ingredient1 = sample_ingredient(user=self.user, name="Garlic,Onions")
            ingredient2=sample_ingredient(user=self.user, name="Onione 2")

            recipe1.ingredients.add(ingredient1)
            recipe2.ingredients.add(ingredient2)

            res = self.client.get(RECIPE_URL, {'ingredients': f"{ingredient1.id},{ingredient2.id}"})

            serializer1=RecipeSerializer(recipe1)
            serializer2 =RecipeSerializer(recipe2)
            serializer3 =RecipeSerializer(recipe3)


            self.assertIn(serializer1.data, res.data)
            self.assertIn(serializer2.data, res.data)
            self.assertNotIn(serializer3.data, res.data)


            

















