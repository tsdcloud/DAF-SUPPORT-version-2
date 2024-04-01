# depenses/serializers.py
from rest_framework import serializers
from .models import FamilyArticle, Article

#  FAMILY ARTICLE SERIALIZER
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
            'date_init',
            'active',
        ]
 
 
# ARTICLE SERIALIZER       
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
            'type_module',
            'site',
            'entite',
        ]
                    
class ArticleListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id',
            'num_ref',
            'label',
            'sigle',
            'type_module',
            'site',
            'entite',
            'date_init',
            'active',
        ]
        
        