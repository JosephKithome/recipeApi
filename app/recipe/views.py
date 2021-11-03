from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient,Recipe
from recipe.serializers import TagSerializer, IngredientSerializer,RecipeSerializer,RecipeDetailSerializer,RecipeImageSerializer
from rest_framework.response import Response


from rest_framework.decorators import action
class  BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                             mixins.ListModelMixin,
                             mixins.CreateModelMixin):
        """Base Viewset for user recipe attributes"""
        authentication_classes =  (TokenAuthentication,)
        permission_classes = (IsAuthenticated,)

        def get_queryset(self):
            """Return objects for the current authenticated user"""
            assigned_only = bool(
                int(self.request.query_params.get("assigned_only", 0))
            )
            queryset = self.queryset
            if assigned_only:
                queryset =queryset.filter(recipe__isnull=False)
            return queryset.filter(user=self.request.user).order_by('-name').distinct()

        def perform_create(self, serializer):
            """Create a new object"""
            serializer.save(user=self.request.user)




class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer 
     


# from rest_framework.renderers import JSONRenderer,TemplateHTMLRenderer
class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # renderer_classes = [TemplateHTMLRenderer]

            
class RecipeViewSet(viewsets.ModelViewSet):    
    """Manage recipes in db"""
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes =(TokenAuthentication,)
    permission_classes =(IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of Integers"""
        return [int(str_id) for str_id in qs.split(',')]


    def get_queryset(self):
        """Return recipe for authenticated user"""
        tags = self.request.query_params.get('tag')
        ingredient = self.request.query_params.get("ingredients")

        if tags:
            tag_ids = self._params_to_ints(tag)
            queryset = queryset.filter(tag__id__in=tag_ids)
        if ingredient:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset=queryset.filter(ingredients__id__in=ingredient_ids)
        queryset = self.queryset
        return queryset.filter(user=self.request.user)


    def get_serializer_class(self):
        """Return appropriate serializer class"""

        if self.action =="retrieve":
            return RecipeDetailSerializer
        elif self.action =='upload_image':
            return RecipeImageSerializer    
        return self.serializer_class  

    # creating recipe endpoints
    def perform_create(self, serializer):
        """Create a new recipe """
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload_image')
    def upload_image(self,request, pk=None):
        """Upload an image to recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)    

        

