from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from store.models import Product
from .serializers import ProductSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework import generics
from rest_framework.views import APIView


@api_view(['GET'])
def api_detail_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)


@api_view(['PUT'])
def api_update_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ProductSerializer(product, request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['success'] = 'update successful'
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def api_delete_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        operation = product.delete()
        data = {}
        if operation:
            data['success'] = 'delete successful'
        else:
            data['failure'] = 'delete failed'
        return Response(data=data)


@api_view(['POST'])
def api_create_view(request):
    if request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApiProductView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination


# class api_detail_view_class(request):
#
#     if request=='GET':
#         product = Product.objects.all()
#         serializer = ProductSerializer(product, many=True)
#         return Response(serializer.data, safe=False)
#
#     elif request.method == 'POST':
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)