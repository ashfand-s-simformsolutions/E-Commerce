from rest_framework import serializers
from store.models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']


class ProductSerializer(serializers.ModelSerializer):

    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'image', 'description']

   

# {
#     "name": "Iphone",
#     "category": 1,
#     "price": "30000",
#     "image": "/Users/ashfand.shaikh/Desktop/iphone.jpg",
#     "description": "This is a phone made by apple"
# }


    # from snippets.models import Snippet
    # from snippets.serializers import SnippetSerializer
    # from rest_framework import generics
    #
    # class SnippetList(generics.ListCreateAPIView):
    #     queryset = Snippet.objects.all()
    #     serializer_class = SnippetSerializer
    #
    # class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    #     queryset = Snippet.objects.all()
    #     serializer_class = SnippetSerializer