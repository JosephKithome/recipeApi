from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient,Recipe
from recipe.serializers import TagSerializer, IngredientSerializer,RecipeSerializer,RecipeDetailSerializer

class  BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                             mixins.ListModelMixin,
                             mixins.CreateModelMixin):
        """Base Viewset for user recipe attributes"""
        authentication_classes =  (TokenAuthentication,)
        permission_classes = (IsAuthenticated,)

        def get_queryset(self):
            """Return objects for the current authenticated user"""
            return self.queryset.filter(user=self.request.user).order_by('-name')

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

    def get_queryset(self):
        """Return recipe for authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""

        if self.action =="retrieve":
            return RecipeDetailSerializer
        return self.serializer_class  
