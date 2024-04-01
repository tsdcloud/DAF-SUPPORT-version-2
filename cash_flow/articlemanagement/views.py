# article management/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from common.middleware import get_email_addressee, send_email
from django.shortcuts import get_object_or_404,render

from django.db import DatabaseError, transaction
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework.decorators import action
from datetime import datetime

from articlemanagement.models import FamilyArticle, Article
from articlemanagement.serializers import ( FamilyArticleSerializer, ArticleSerializer,
                                            FamilyArticleCreateSerializer, ArticleCreateSerializer,
                                            FamilyArticleListingSerializer, ArticleListingSerializer)
from common.permissions import IsDeactivate, IsActivate
from articlemanagement .permissions import (IsAddFamilyArticle, IsViewAllFamilyArticle,
                                   IsChangeFamilyArticle, IsDestroyFamilyArticle,
                                   IsRestoreFamilyArticle, IsAddArticle,IsViewAllArticle,
                                   IsChangeArticle, IsDestroyArticle,IsRestoreArticle)

class FamilyArticleViewSet(viewsets.ModelViewSet):
    # queryset = FamilyArticle.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return FamilyArticleCreateSerializer
        if self.action == 'list':
            return FamilyArticleListingSerializer
        if self.action == 'retrieve':
            return FamilyArticleCreateSerializer
        if self.action == 'update':
            return FamilyArticleCreateSerializer
        return FamilyArticleSerializer
    
    
    def get_permissions(self):
        """ define permissions """
        if self.action == 'create':
            self.permission_classes = [IsAddFamilyArticle]
        elif self.action == 'list':
            self.permission_classes = [IsViewAllFamilyArticle]
        elif self.action == 'retrieve':
            self.permission_classes = [IsViewAllFamilyArticle]
        elif self.action == 'update':
            self.permission_classes = [IsChangeFamilyArticle]
        elif self.action == 'destroy':
            self.permission_classes = [IsDestroyFamilyArticle]
        elif self.action == 'restore':
            self.permission_classes = [IsRestoreFamilyArticle]
        else:
            self.permission_classes = [IsDeactivate]
        return super().get_permissions()
    
    
    def get_queryset(self):
        """ define queryset """
        # Remplacez votre code actuel à la ligne 65 dans views.py par le suivant
        if self.request.infoUser and 'member' in self.request.infoUser and 'is_superuser' in self.request.infoUser['member']:
            if self.request.infoUser['member']['is_superuser'] is True:
                queryset = FamilyArticle.objects.all()
            else:
                queryset = FamilyArticle.objects.filter(is_active=True)
        else:
            # Gérez le cas où self.request.infoUser est None ou ne contient pas les clés attendues
            queryset = FamilyArticle.objects.filter(is_active=True)
        return queryset


    def get_object(self):
        """ define object on detail url """
        queryset = self.get_queryset()
        try:
            obj = get_object_or_404(queryset, id=self.kwargs["pk"])
        except ValidationError:
            raise Http404("detail not found")
        return obj


    def create(self, request, *args, **kwargs):
        """create an object"""
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
       
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    family_article = FamilyArticle.create_family_article(
                        label=serializer.validated_data['label'],
                        sigle=serializer.validated_data['sigle'],
                        type_module=serializer.validated_data['type_module'],
                        site=serializer.validated_data['site'],
                        entite=serializer.validated_data['entite'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                family_article = None

            headers = self.get_success_headers(serializer.data)
            
            return Response(
                FamilyArticleListingSerializer(family_article).data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Erreur lors de la création de la famille d'article"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
              
    
    def list(self, request, *args, **kwargs):
        """
        This view intends to render all expenses sheets.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        
        queryset = self.get_queryset()
        # Ajout historique du listing
        # if queryset:
        #     FamilyArticle.create_histry_listing(
        #                 user=request.infoUser.get('id')
        #             )
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    def retrieve(self, request, pk=None,*args, **kwargs):
        """get an object"""
        
        try:
            # Récupérer l'objet individuel de la base de données en utilisant l'identifiant fourni dans l'URL
            obj = self.get_object()

            # Sérialiser l'objet récupéré en utilisant le sérialiseur approprié pour la réponse détaillée
            serializer = self.get_serializer(obj)

            # Retourner la réponse avec le statut HTTP 200 OK et les données sérialisées
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404:
            # Gérer le cas où l'objet n'est pas trouvé dans la base de données
            return Response({"detail": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Gérer les exceptions génériques et renvoyer une réponse d'erreur avec le statut HTTP 500 Internal Server Error
            return Response({"detail": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def update(self, request, pk=None, *args, **kwargs):
        # Logique pour mettre à jour un objet complet
        serializer = self.get_serializer(data=self.request.data)
        
       
        # if serializer.is_valid():
        if serializer.is_valid(raise_exception=True):
            try:
                with transaction.atomic():
                    family_article = FamilyArticle.update_family_article(
                        cls = self,
                        family_article_id = pk,
                        label=serializer.validated_data['label'],
                        sigle=serializer.validated_data['sigle'],
                        type_module=serializer.validated_data['type_module'],
                        site=serializer.validated_data['site'],
                        entite=serializer.validated_data['entite'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                family_article = None

            headers = self.get_success_headers(serializer.data)
            return Response(
                FamilyArticleListingSerializer(family_article).data,
                status=status.HTTP_200_OK,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Error when creating expense sheet"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
    def destroy(self, request, pk=None):
        """ Action pour supprimer une fiche de dépenses """
        family_article = self.get_object()
        user_qs = request.infoUser.get('id')
        print(f"{user_qs}")
        family_article.delete_family_article(user=user_qs, family_article_id = pk)
        family_article = self.get_object()
        return Response(
            FamilyArticleListingSerializer(
                family_article,
                context={"request": request, "family_article": family_article}
            ).data,
            status=status.HTTP_200_OK
        )
        
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None, ):
        """ Action pour restorer une fiche de dépenses """
        family_article = self.get_object()
        user_qs = request.infoUser.get('id')
        family_article.restore_family_article(user=user_qs, family_article_id = pk)
        family_article = self.get_object()
        return Response(
            FamilyArticleListingSerializer(
                family_article,
                context={"request": request, "family_article": family_article}
            ).data,
            status=status.HTTP_200_OK
        )


class ArticleViewSet(viewsets.ModelViewSet):
    # queryset = FamilyArticle.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreateSerializer
        if self.action == 'list':
            return ArticleListingSerializer
        if self.action == 'retrieve':
            return ArticleCreateSerializer
        if self.action == 'update':
            return ArticleCreateSerializer
        return ArticleSerializer
    
    
    def get_permissions(self):
        """ define permissions """
        if self.action == 'create':
            self.permission_classes = [IsAddArticle]
        elif self.action == 'list':
            self.permission_classes = [IsViewAllArticle]
        elif self.action == 'retrieve':
            self.permission_classes = [IsViewAllArticle]
        elif self.action == 'update':
            self.permission_classes = [IsChangeArticle]
        elif self.action == 'destroy':
            self.permission_classes = [IsDestroyArticle]
        elif self.action == 'restore':
            self.permission_classes = [IsRestoreArticle]
        else:
            self.permission_classes = [IsDeactivate]
        return super().get_permissions()
    
    
    def get_queryset(self):
        """ define queryset """
        # Remplacez votre code actuel à la ligne 65 dans views.py par le suivant
        if self.request.infoUser and 'member' in self.request.infoUser and 'is_superuser' in self.request.infoUser['member']:
            if self.request.infoUser['member']['is_superuser'] is True:
                queryset = Article.objects.all()
            else:
                queryset = Article.objects.filter(is_active=True)
        else:
            # Gérez le cas où self.request.infoUser est None ou ne contient pas les clés attendues
            queryset = Article.objects.filter(is_active=True)
        return queryset


    def get_object(self):
        """ define object on detail url """
        queryset = self.get_queryset()
        try:
            obj = get_object_or_404(queryset, id=self.kwargs["pk"])
        except ValidationError:
            raise Http404("detail not found")
        return obj


    def create(self, request, *args, **kwargs):
        """create an object"""
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
       
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    family_article = Article.create_family_article(
                        family_article_id=serializer.validated_data['family_article_id'],
                        label=serializer.validated_data['label'],
                        sigle=serializer.validated_data['sigle'],
                        description=serializer.validated_data['description'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                family_article = None

            headers = self.get_success_headers(serializer.data)
            
            return Response(
                ArticleListingSerializer(family_article).data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Erreur lors de la création de la famille d'article"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
              
    
    def list(self, request, *args, **kwargs):
        """
        This view intends to render all expenses sheets.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        
        queryset = self.get_queryset()
        # Ajout historique du listing
        # if queryset:
        #     FamilyArticle.create_histry_listing(
        #                 user=request.infoUser.get('id')
        #             )
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    def retrieve(self, request, pk=None,*args, **kwargs):
        """get an object"""
        
        try:
            # Récupérer l'objet individuel de la base de données en utilisant l'identifiant fourni dans l'URL
            obj = self.get_object()

            # Sérialiser l'objet récupéré en utilisant le sérialiseur approprié pour la réponse détaillée
            serializer = self.get_serializer(obj)

            # Retourner la réponse avec le statut HTTP 200 OK et les données sérialisées
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404:
            # Gérer le cas où l'objet n'est pas trouvé dans la base de données
            return Response({"detail": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Gérer les exceptions génériques et renvoyer une réponse d'erreur avec le statut HTTP 500 Internal Server Error
            return Response({"detail": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def update(self, request, pk=None, *args, **kwargs):
        # Logique pour mettre à jour un objet complet
        serializer = self.get_serializer(data=self.request.data)
        
       
        # if serializer.is_valid():
        if serializer.is_valid(raise_exception=True):
            try:
                with transaction.atomic():
                    family_article = Article.update_article(
                        cls = self,
                        article_id = pk,
                        family_article_id=serializer.validated_data['family_article_id'],
                        label=serializer.validated_data['label'],
                        sigle=serializer.validated_data['sigle'],
                        description=serializer.validated_data['description'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                family_article = None

            headers = self.get_success_headers(serializer.data)
            return Response(
                FamilyArticleListingSerializer(family_article).data,
                status=status.HTTP_200_OK,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Error when updated article"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
    def destroy(self, request, pk=None):
        """ Action pour supprimer un article """
        article = self.get_object()
        user_qs = request.infoUser.get('id')
        article.delete_article(user=user_qs, articleid = pk)
        article = self.get_object()
        return Response(
            ArticleListingSerializer(
                article,
                context={"request": request, "article": article}
            ).data,
            status=status.HTTP_200_OK
        )
        
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None, ):
        """ Action pour restorer un article """
        article = self.get_object()
        user_qs = request.infoUser.get('id')
        article.restore_article(user=user_qs, article_id = pk)
        article = self.get_object()
        return Response(
            ArticleListingSerializer(
                article,
                context={"request": request, "article": article}
            ).data,
            status=status.HTTP_200_OK
        )


