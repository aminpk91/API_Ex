from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Author, Article, ArticleCategory, Chapter, Comment


class UserSerializerNested(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "is_staff"]


class AuthorSerializer(serializers.ModelSerializer):

    user = UserSerializerNested()

    class Meta:
        model = Author
        fields = ['user', 'age', 'created_at']


class ArticleListSerializer(serializers.ModelSerializer):
    number_of_comments = serializers.SerializerMethodField()

    class Meta:
        model = Article
        exclude = ["id"]

    def get_number_of_comments(self, obj):
        return obj.comments.all().values()


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = "__all__"


class CommentSerializer(serializers.Serializer):
    user = serializers.CharField()
    content = serializers.CharField()

    def create(self, validated_data, **kwargs):
        article_id = int(self.context.get("article_id"))
        print(article_id)
        return Comment.objects.create(article_id=article_id, **validated_data)

    def update(self, instance, validated_data):
        instance.user = validated_data.get("user", instance.user)
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        return instance


class ArticleDetailSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True)
    comment_set = CommentSerializer(many=True)

    class Meta:
        model = Article
        fields = "__all__"
