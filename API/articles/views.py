from django.http import Http404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from django.shortcuts import get_object_or_404

from .models import Author, Article, Comment
from .serializers import AuthorSerializer, ArticleListSerializer, ArticleDetailSerializer, CommentSerializer


class AuthorList(APIView):

    def get(self, request, fotmat=None):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)


class AuthorDetail(APIView):
    def get_object(self, pk):
        try:
            return Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        author = self.get_object(pk)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)


class ArticleListView(ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer


class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer


class CommentView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        article_id = request.query_params.get("article", None)

        if not article_id:
            return Response({
                "successful": False,
                "err": True,
                "message": "need article id for comment"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not Article.objects.filter(id=article_id).exists():
            return Response({
                "successful": False,
                "err": True,
                "message": "article id not valid"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentSerializer(
            data=request.data, context={"article_id": article_id, "request": request})

        if serializer.is_valid():
            serializer.save()

            return Response({
                "successful": True,
                "err": False,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "successful": False,
            "err": True,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        serializer = CommentSerializer(comment, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({
                "successful": True,
                "err": False,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "successful": False,
            "err": True,
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.delete()

        return Response({
            "successful": True,
            "err": False,
            "messeage": "successfully deleted"
        }, status=status.HTTP_204_NO_CONTENT)
