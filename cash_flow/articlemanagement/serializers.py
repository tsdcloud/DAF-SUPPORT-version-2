# Management article/serializers.py
from rest_framework import serializers
from .models import FamilyArticle, Article
from common.constances import TypeProduit, Module

# FAMILY ARTICLE SERIALIZERS
class FamilyArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyArticle
        fields = '__all__'

class FamilyArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyArticle
        fields = [
            'label',
            'sigle',
            'type_module',
            'site',
            'entite',
        ]

class FamilyArticleListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyArticle
        fields = [
            'id',
            'num_ref',
            'label',
            'sigle',
            'type_module',
            'site',
            'entite',
            'time_created',
            'is_active',
        ]

# ARTICLE SERIALIZERS
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'label',
            'sigle',
            'family_article_id',
            'description',
        ]

class ArticleListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id',
            'num_ref',
            'family_article_id',
            'label',
            'sigle',
            'description',
            'time_created',
            'create_by',
            'is_active',
        ]