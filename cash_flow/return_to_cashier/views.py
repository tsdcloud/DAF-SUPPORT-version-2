from django.shortcuts import render
# depenses/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from common.middleware import get_email_addressee, send_email
from django.shortcuts import get_object_or_404

from django.db import DatabaseError, transaction
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework.decorators import action
from datetime import datetime

from return_to_cashier.models import ReturnToCashier
from return_to_cashier.serializers import (ReturnToCashierSerializer, ReturnToCashierCreateSerializer,
                                  ReturnToCashierListingSerializer, ReturnToCashierDetailSerializer,
                                  ReturnToCashierValidationSerializer, ReturnToCashierValidationCodeSerializer)
from common.permissions import IsDeactivate, IsActivate
from return_to_cashier .permissions import (IsAddReturnToCashier, IsChangeReturnToCashier,
                                   IsDestroyReturnToCashier, IsRestoreReturnToCashier,
                                   IsViewDetailReturnToCashier, IsViewAllReturnToCashier,
                                   IsValidateReturnToCashier, IsRejecteReturnToCashier)

class ReturnToCashierViewSet(viewsets.ModelViewSet):
    # queryset = ReturnToCashier.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ReturnToCashierCreateSerializer
        if self.action == 'list':
            return ReturnToCashierListingSerializer
        if self.action == 'retrieve':
            return ReturnToCashierDetailSerializer
        if self.action == 'update':
            return ReturnToCashierCreateSerializer
        if self.action == 'partial_update':
            print("partial_update")
            return ReturnToCashierValidationSerializer
        if self.action == 'code_validation':
            return ReturnToCashierValidationCodeSerializer
        return ReturnToCashierSerializer
    
    
    def get_permissions(self):
        """ define permissions """
        if self.action == 'create':
            self.permission_classes = [IsAddReturnToCashier]
        elif self.action == 'list':
            self.permission_classes = [IsViewAllReturnToCashier]
        elif self.action == 'retrieve':
            self.permission_classes = [IsViewDetailReturnToCashier]
        elif self.action == 'update':
            self.permission_classes = [IsChangeReturnToCashier]
        elif self.action in ['partial_update', "rejection"]:
            self.permission_classes = [IsValidateReturnToCashier]
        elif self.action == 'partial_update':
            self.permission_classes = [IsValidateReturnToCashier]
        elif self.action == 'rejection':
            self.permission_classes = [IsRejecteReturnToCashier]
        elif self.action == 'destroy':
            self.permission_classes = [IsDestroyReturnToCashier]
        elif self.action == 'restore':
            self.permission_classes = [IsRestoreReturnToCashier]
        else:
            self.permission_classes = [IsDeactivate]
            # self.permission_classes = [IsActivate]
        return super().get_permissions()
    
    
    def get_queryset(self):
        """ define queryset """
        # Remplacez votre code actuel à la ligne 65 dans views.py par le suivant
        if self.request.infoUser and 'member' in self.request.infoUser and 'is_superuser' in self.request.infoUser['member']:
            if self.request.infoUser['member']['is_superuser'] is True:
                queryset = ReturnToCashier.objects.all()
            else:
                queryset = ReturnToCashier.objects.filter(is_active=True)
        else:
            # Gérez le cas où self.request.infoUser est None ou ne contient pas les clés attendues
            queryset = ReturnToCashier.objects.filter(is_active=True)
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
                    return_to_cashier = ReturnToCashier.create_return_to_cashier(
                        
                        expense_sheet_id=serializer.validated_data['expense_sheet_id'],
                        remaining_balance=serializer.validated_data['remaining_balance'],
                        description=serializer.validated_data['description'],
                        payment_method=serializer.validated_data['payment_method'],
                        num_dossier=serializer.validated_data['num_dossier'],
                        site=serializer.validated_data['site'],
                        entite=serializer.validated_data['entite'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                return_to_cashier = None

            headers = self.get_success_headers(serializer.data)
            # email
            addressee = get_email_addressee(return_to_cashier.employer_conformite)
            addressee = serializer.validated_data['employer_conformite']
            print(addressee)
            addressee = get_email_addressee(addressee)
            addressee = get_email_addressee(serializer.validated_data['employer_conformite'])
            addressee = [addressee]
            # send_email(
            #     subject = f"Creation de fiche de dépense numéro: {return_to_cashier.num_ref}",
            #     message = f"L'employé {request.infoUser.get('last_name')} { request.infoUser.get('first_name')}  
            #                 une fiche importante qui nécessite votre validation. Pour procéder, veuillez suivre le lien http://bfclimited.com /{return_to_cashier.id}.Merci" ,
            #     recipient_list = addressee
            # )
            return Response(
                ReturnToCashierListingSerializer(return_to_cashier).data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Erreur lors de la création de la fiche de dépenses"},
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
        #     ReturnToCashier.create_histry_listing(
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
        
        if serializer.is_valid(raise_exception=True):
            try:
                with transaction.atomic():
                    return_to_cashier = ReturnToCashier.update_return_to_cashier(
                        return_to_cashier_id = pk,
                        expense_sheet_id=serializer.validated_data['expense_sheet_id'],
                        remaining_balance=serializer.validated_data['remaining_balance'],
                        description=serializer.validated_data['description'],
                        payment_method=serializer.validated_data['payment_method'],
                        num_dossier=serializer.validated_data['num_dossier'],
                        site=serializer.validated_data['site'],
                        entite=serializer.validated_data['entite'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                return_to_cashier = None

            headers = self.get_success_headers(serializer.data)
            return Response(
                ReturnToCashierDetailSerializer(return_to_cashier).data,
                status=status.HTTP_200_OK,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Error when creating expense sheet"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
    
    def partial_update(self, request, pk=None, *args, **kwargs):
        # Logique pour mettre à jour un objet complet
        serializer = self.get_serializer(data=self.request.data)
        
        if serializer.is_valid(raise_exception=True):
            try:
                with transaction.atomic():
                    return_to_cashier = ReturnToCashier.validate_return_to_cashier(
                        return_to_cashier_id=pk,
                        observation=serializer.validated_data['description'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError as e:
                print(f"Database error during update: {e}")
                return_to_cashier = None

            if return_to_cashier:
                return_to_cashier = self.get_object()
                return Response(
                    # return_to_cashier.data,
                    ReturnToCashierDetailSerializer(return_to_cashier).data,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "This action cannot be performed. Check user, expense status or your observation"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {"detail": "Votre formulaire est vide"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
    # @action(detail=False, methods=['PATCH'])
    @action(detail=True, methods=['patch'])
    def rejection(self, request, pk=None, *args, **kwargs):
        # Logique pour mettre à jour un objet complet
        serializer = ReturnToCashierValidationSerializer(data=self.request.data)
        
        if serializer.is_valid(raise_exception=True):
            try:
                with transaction.atomic():
                    return_to_cashier = ReturnToCashier.rejection_return_to_cashier(
                        return_to_cashier_id=pk,
                        observation=serializer.validated_data['description'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError as e:
                print(f"Database error during update: {e}")
                return_to_cashier = None

            if return_to_cashier:
                return_to_cashier = self.get_object()
                return Response(
                    # return_to_cashier.data,
                    ReturnToCashierDetailSerializer(return_to_cashier).data,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "This action cannot be performed. Check user, expense status or your observation"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {"detail": "Your form is not empty"},
                status=status.HTTP_400_BAD_REQUEST
            )
            

    def destroy(self, request, pk=None):
        """ Action pour supprimer une fiche de dépenses """
        print("ok delete")
        ReturnToCashier = self.get_object()
        user_qs = request.infoUser.get('id')
        print(f"{user_qs}")
        # ReturnToCashier.delete_return_to_cashier(self, user=user_qs.first)
        ReturnToCashier.delete_return_to_cashier(user=user_qs, return_to_cashier_id = pk)
        ReturnToCashier = self.get_object()
        return Response(
            ReturnToCashierDetailSerializer(
                ReturnToCashier,
                context={"request": request, "ReturnToCashier": ReturnToCashier}
            ).data,
            status=status.HTTP_200_OK
        )
    
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None, ):
        """ Action pour restorer une fiche de dépenses """
        ReturnToCashier = self.get_object()
        user_qs = request.infoUser.get('id')
        print(f"id user : {user_qs}")
        print(f"id ReturnToCashier : {pk}")
        ReturnToCashier.restore_return_to_cashier(user=user_qs, return_to_cashier_id = pk)
        ReturnToCashier = self.get_object()
        return Response(
            ReturnToCashierDetailSerializer(
                ReturnToCashier,
                context={"request": request, "ReturnToCashier": ReturnToCashier}
            ).data,
            status=status.HTTP_200_OK
        )


   

# Create your views here.
