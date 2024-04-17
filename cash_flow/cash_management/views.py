# cash transaction/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from common.middleware import get_email_addressee, send_email
from django.shortcuts import get_object_or_404, render

from django.db import DatabaseError, transaction
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework.decorators import action
from datetime import datetime
import random
from django.utils import timezone
from datetime import timedelta
from depenses.models import ExpenseSheet

from cash_management.models import CashTransaction
from cash_management.serializers import (CashTransactionSerializer, CashTransactionCreateSerializer,
                                  CashTransactionListingSerializer, CashTransactionDetailSerializer,
                                  CashTransactionValidationSerializer, CashTransactionValidationCodeSerializer,
                                  CashTransactionGenerateCodeSerializer)
                                #   DenominationSerializer,DenominationCreateSerializer,DenominationListingSerializer,
                                #   DenominationCreateSerializer,
                                #   CurrencySerializer,CurrencyCreateSerializer,CurrencyListingSerializer,
                                #   CurrencyCreateSerializer,
                                #   CashRegisterSerializer,CashRegisterCreateSerializer,
                                #   CashRegisterListingSerializer, CashRegisterDetailSerializer,
                                #   CashRegisterValidationSerializer)
from common.permissions import IsDeactivate, IsActivate
from cash_management .permissions import (IsAddCashTransaction, IsChangeCashTransaction,
                                   IsDestroyCashTransaction, IsRestoreCashTransaction,
                                   IsViewDetailCashTransaction, IsViewAllCashTransaction,
                                   IsValidateCashTransaction, IsRejecteCashTransaction,
                                   IsGenerateCodeCashTransaction,IsValidateCodeCashTransaction)

class CashTransactionViewSet(viewsets.ModelViewSet):
    # queryset = CashTransaction.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CashTransactionCreateSerializer
        if self.action == 'list':
            return CashTransactionListingSerializer
        if self.action == 'retrieve':
            return CashTransactionDetailSerializer
        if self.action == 'update':
            return CashTransactionCreateSerializer
        if self.action == 'partial_update':
            return CashTransactionValidationCodeSerializer
        if self.action == 'code_validation':
            return CashTransactionValidationCodeSerializer
        if self.action == 'generate_code':
            return CashTransactionGenerateCodeSerializer
        return CashTransactionSerializer
    
    
    def get_permissions(self):
        """ define permissions """
        if self.action == 'create':
            self.permission_classes = [IsAddCashTransaction]
        elif self.action == 'list':
            self.permission_classes = [IsViewAllCashTransaction]
        elif self.action == 'retrieve':
            self.permission_classes = [IsViewDetailCashTransaction]
        elif self.action == 'update':
            self.permission_classes = [IsChangeCashTransaction]
        elif self.action in ['partial_update', "rejection"]:
            self.permission_classes = [IsValidateCashTransaction]
        elif self.action == 'partial_update':
            self.permission_classes = [IsValidateCashTransaction]
        elif self.action == 'rejection':
            self.permission_classes = [IsRejecteCashTransaction]
        elif self.action == 'destroy':
            self.permission_classes = [IsDestroyCashTransaction]
        elif self.action == 'restore':
            self.permission_classes = [IsRestoreCashTransaction]
        elif self.action == 'generate_code':
            self.permission_classes = [IsGenerateCodeCashTransaction]
        else:
            self.permission_classes = [IsDeactivate]
        return super().get_permissions()
    
    
    def get_queryset(self):
        """ define queryset """
        # Remplacez votre code actuel à la ligne 65 dans views.py par le suivant
        if self.request.infoUser and 'member' in self.request.infoUser and 'is_superuser' in self.request.infoUser['member']:
            if self.request.infoUser['member']['is_superuser'] is True:
                queryset = CashTransaction.objects.all()
            else:
                queryset = CashTransaction.objects.filter(is_active=True)
        else:
            # Gérez le cas où self.request.infoUser est None ou ne contient pas les clés attendues
            queryset = CashTransaction.objects.filter(is_active=True)
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
        print("ok")
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data['module'])
        
        if serializer.validated_data['module'] == 'DEPENSE':
                check = ExpenseSheet.check_expense_sheet(expense_sheet_id=serializer.validated_data['item_id'])
                if check == False:
                    return Response({"detail": f"No expense sheet"}, status=status.HTTP_400_BAD_REQUEST)
        elif cash_transaction.module == 'RECETTE':
            pass
        elif cash_transaction.module == 'RETOUR CAISSE':
            pass
        elif cash_transaction.module == 'APPROVISIONNEMENT CAISSE':
            pass
    
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    cash_transaction = CashTransaction.create_cash_transaction(
                        employer_beneficiaire=serializer.validated_data['employer_beneficiaire'],
                        cashier_id=serializer.validated_data['cashier_id'],
                        montant=serializer.validated_data['montant'],
                        transaction_type=serializer.validated_data['transaction_type'],
                        module=serializer.validated_data['module'],
                        item_id=serializer.validated_data['item_id'],
                        description=serializer.validated_data['description'],
                        num_dossier=serializer.validated_data['num_dossier'],
                        site=serializer.validated_data['site'],
                        entite=serializer.validated_data['entite'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                cash_transaction = None

            headers = self.get_success_headers(serializer.data)
            # email
            # addressee = get_email_addressee(cash_transaction.employer_conformite)
            # addressee = serializer.validated_data['employer_conformite']
            # print(addressee)
            # addressee = get_email_addressee(addressee)
            # addressee = get_email_addressee(serializer.validated_data['employer_conformite'])
            # addressee = [addressee]
            # send_email(
            #     subject = f"Creation de fiche de dépense numéro: {cash_transaction.num_ref}",
            #     message = f"L'employé {request.infoUser.get('last_name')} { request.infoUser.get('first_name')}  
            #                 une fiche importante qui nécessite votre validation. Pour procéder, veuillez suivre le lien http://bfclimited.com /{cash_transaction.id}.Merci" ,
            #     recipient_list = addressee
            # )
            return Response(
                CashTransactionListingSerializer(cash_transaction).data,
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
        #     CashTransaction.create_histry_listing(
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
                    cash_transaction = CashTransaction.update_cash_transaction(
                        cls = self,
                        cash_transaction_id = pk,
                        employer_initiateur=request.infoUser.get('id'),
                        employer_beneficiaire=serializer.validated_data['employer_beneficiaire'],
                        employer_conformite=serializer.validated_data['employer_conformite'],
                        employer_budgetaire=serializer.validated_data['employer_budgetaire'],
                        employer_ordonnateur=serializer.validated_data['employer_ordonnateur'],
                        description=serializer.validated_data['description'],
                        num_dossier=serializer.validated_data['num_dossier'],
                        montant=serializer.validated_data['montant'],
                        site=serializer.validated_data['site'],
                        entite=serializer.validated_data['entite'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                cash_transaction = None

            headers = self.get_success_headers(serializer.data)
            return Response(
                CashTransactionDetailSerializer(cash_transaction).data,
                status=status.HTTP_200_OK,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Error when creating expense sheet"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
    
    @action(detail=True, methods=['patch'])
    def generate_code(self, request, pk=None, *args, **kwargs):
        # serializer = CashTransactionValidationSerializer(data=self.request.data)
        serializer = self.get_serializer(data=self.request.data)
        
        if serializer.is_valid(raise_exception=True):
            code_validation = str(random.randint(1000, 9999))
            expiration_time = timezone.now() + timedelta(minutes=5)
            try:
                with transaction.atomic():
                    cash_transaction = CashTransaction.generate_code_cash_transaction(
                        # cls = self,
                        cash_transaction_id = pk,
                        code_validation=code_validation,
                        expiration_time=expiration_time,
                        user=request.infoUser.get('id')
                    )
                    print(code_validation)
                    print(expiration_time)
            except DatabaseError:
                cash_transaction = None

            headers = self.get_success_headers(serializer.data)
            return Response(
                # CashTransactionDetailSerializer(cash_transaction).data,
                {'Message': 'code is correctly generated'},
                status=status.HTTP_200_OK,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Error when creating code validation"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def partial_update(self, request, pk=None, *args, **kwargs):
        # Logique pour mettre à jour un objet complet

        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            
            try:
                with transaction.atomic():
                    cash_transaction = CashTransaction.validate_cash_transaction(
                        cash_transaction_id=pk,
                        code_validation=serializer.validated_data['code_validation'],
                        user=request.infoUser.get('id')
                    )
                    if cash_transaction== None:
                        return Response(
                            {"detail": "Votre mot de pass est incorrecte ou il a déja expiré!"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    else :
                        return Response(
                            # cash_transaction.data,
                            CashTransactionDetailSerializer(cash_transaction).data,
                            status=status.HTTP_200_OK
                        )
                        
            except DatabaseError as e:
                print(f"Database error during update: {e}")
                cash_transaction = None
        else:
            return Response(
                {"detail": "Votre formulaire est vide"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
    # @action(detail=False, methods=['PATCH'])
    # @action(detail=True, methods=['patch'])
    # def rejection(self, request, pk=None, *args, **kwargs):
    #     # Logique pour mettre à jour un objet complet
    #     serializer = CashTransactionValidationSerializer(data=self.request.data)
        
    #     if serializer.is_valid(raise_exception=True):
    #         try:
    #             with transaction.atomic():
    #                 cash_transaction = CashTransaction.rejection_cash_transaction(
    #                     cash_transaction_id=pk,
    #                     observation=serializer.validated_data['description'],
    #                     user=request.infoUser.get('id')
    #                 )
    #         except DatabaseError as e:
    #             print(f"Database error during update: {e}")
    #             cash_transaction = None

    #         if cash_transaction:
    #             cash_transaction = self.get_object()
    #             return Response(
    #                 # cash_transaction.data,
    #                 CashTransactionDetailSerializer(cash_transaction).data,
    #                 status=status.HTTP_200_OK
    #             )
    #         else:
    #             return Response(
    #                 {"detail": "This action cannot be performed. Check user, expense status or your observation"},
    #                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #             )
    #     else:
    #         return Response(
    #             {"detail": "Your form is not empty"},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
            
    

    
    
    def destroy(self, request, pk=None):
        """ Action pour supprimer une fiche de dépenses """
        print("ok delete")
        CashTransaction = self.get_object()
        user_qs = request.infoUser.get('id')
        print(f"{user_qs}")
        # CashTransaction.delete_cash_transaction(self, user=user_qs.first)
        CashTransaction.delete_cash_transaction(user=user_qs, cash_transaction_id = pk)
        CashTransaction = self.get_object()
        return Response(
            CashTransactionDetailSerializer(
                CashTransaction,
                context={"request": request, "CashTransaction": CashTransaction}
            ).data,
            status=status.HTTP_200_OK
        )
    
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None, ):
        """ Action pour restorer une fiche de dépenses """
        CashTransaction = self.get_object()
        user_qs = request.infoUser.get('id')
        print(f"id user : {user_qs}")
        print(f"id CashTransaction : {pk}")
        CashTransaction.restore_cash_transaction(user=user_qs, cash_transaction_id = pk)
        CashTransaction = self.get_object()
        return Response(
            CashTransactionDetailSerializer(
                CashTransaction,
                context={"request": request, "CashTransaction": CashTransaction}
            ).data,
            status=status.HTTP_200_OK
        )


# ViewSets define the view behavior.
# class DenominationViewSet(viewsets.ModelViewSet):
#     queryset = Denomination.objects.all()
#     serializer_class = DenominationSerializer
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return DenominationCreateSerializer
#         if self.action == 'list':
#             return DenominationListingSerializer
#         if self.action == 'retrieve':
#             return DenominationListingSerializer
#         if self.action == 'update':
#             return DenominationCreateSerializer
#         return DenominationSerializer
    
    
#     def get_permissions(self):
#         """ define permissions """
#         if self.action == 'create':
#             self.permission_classes = [IsAddDenomination]
#         elif self.action == 'list':
#             self.permission_classes = [IsViewAllDenomination]
#         elif self.action == 'retrieve':
#             self.permission_classes = [IsViewAllDenomination]
#         elif self.action == 'update':
#             self.permission_classes = [IsChangeDenomination]
#         elif self.action == 'destroy':
#             self.permission_classes = [IsDestroyDenomination]
#         elif self.action == 'restore':
#             self.permission_classes = [IsRestoreDenomination]
#         else:
#             self.permission_classes = [IsDeactivate]
#         return super().get_permissions()
    
    
#     def get_queryset(self):
#         """ define queryset """
#         # Remplacez votre code actuel à la ligne 65 dans views.py par le suivant
#         if self.request.infoUser and 'member' in self.request.infoUser and 'is_superuser' in self.request.infoUser['member']:
#             if self.request.infoUser['member']['is_superuser'] is True:
#                 queryset = Denomination.objects.all()
#             else:
#                 queryset = Denomination.objects.filter(is_active=True)
#         else:
#             # Gérez le cas où self.request.infoUser est None ou ne contient pas les clés attendues
#             queryset = Denomination.objects.filter(is_active=True)
#         return queryset


#     def get_object(self):
#         """ define object on detail url """
#         queryset = self.get_queryset()
#         try:
#             obj = get_object_or_404(queryset, id=self.kwargs["pk"])
#         except ValidationError:
#             raise Http404("detail not found")
#         return obj


#     def create(self, request, *args, **kwargs):
#         """create an object"""
#         serializer = self.get_serializer(data=self.request.data)
#         serializer.is_valid(raise_exception=True)
       
#         if serializer.is_valid():
#             try:
#                 with transaction.atomic():
#                     family_article = Denomination.create_family_article(
#                         label=serializer.validated_data['label'],
#                         sigle=serializer.validated_data['sigle'],
#                         type_module=serializer.validated_data['type_module'],
#                         site=serializer.validated_data['site'],
#                         entite=serializer.validated_data['entite'],
#                         user=request.infoUser.get('id')
#                     )
#             except DatabaseError:
#                 family_article = None

#             headers = self.get_success_headers(serializer.data)
            
#             return Response(
#                 DenominationListingSerializer(family_article).data,
#                 status=status.HTTP_201_CREATED,
#                 headers=headers
#             )
#         else:
#             return Response(
#                 {"detail": "Erreur lors de la création de la famille d'article"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
              
    
#     def list(self, request, *args, **kwargs):
#         """
#         This view intends to render all family article sheets.
#         :param request:
#         :param args:
#         :param kwargs:
#         :return:
#         """
        
#         queryset = self.get_queryset()
            
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)

    
#     def retrieve(self, request, pk=None,*args, **kwargs):
#         """get an object"""
#         try:
#             # Récupérer l'objet individuel de la base de données en utilisant l'identifiant fourni dans l'URL
#             obj = self.get_object()

#             # Sérialiser l'objet récupéré en utilisant le sérialiseur approprié pour la réponse détaillée
#             serializer = self.get_serializer(obj)

#             # Retourner la réponse avec le statut HTTP 200 OK et les données sérialisées
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Http404:
#             # Gérer le cas où l'objet n'est pas trouvé dans la base de données
#             return Response({"detail": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             # Gérer les exceptions génériques et renvoyer une réponse d'erreur avec le statut HTTP 500 Internal Server Error
#             return Response({"detail": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#     def update(self, request, pk=None, *args, **kwargs):
#         # Logique pour mettre à jour un objet complet
#         serializer = self.get_serializer(data=self.request.data)
        
       
#         # if serializer.is_valid():
#         if serializer.is_valid(raise_exception=True):
#             try:
#                 with transaction.atomic():
#                     family_article = Denomination.update_family_article(
#                         cls = self,
#                         family_article_id = pk,
#                         label=serializer.validated_data['label'],
#                         sigle=serializer.validated_data['sigle'],
#                         type_module=serializer.validated_data['type_module'],
#                         site=serializer.validated_data['site'],
#                         entite=serializer.validated_data['entite'],
#                         user=request.infoUser.get('id')
#                     )
#             except DatabaseError:
#                 family_article = None

#             headers = self.get_success_headers(serializer.data)
#             return Response(
#                 DenominationListingSerializer(family_article).data,
#                 status=status.HTTP_200_OK,
#                 headers=headers
#             )
#         else:
#             return Response(
#                 {"detail": "Error when creating family article"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
    
#     def destroy(self, request, pk=None):
#         """ Action pour supprimer une fiche de dépenses """
#         family_article = self.get_object()
#         user_qs = request.infoUser.get('id')
#         print(f"{user_qs}")
#         family_article.delete_family_article(user=user_qs, family_article_id = pk)
#         family_article = self.get_object()
#         return Response(
#             DenominationListingSerializer(
#                 family_article,
#                 context={"request": request, "family_article": family_article}
#             ).data,
#             status=status.HTTP_200_OK
#         )
        
#     @action(detail=True, methods=['post'])
#     def restore(self, request, pk=None, ):
#         """ Action pour restorer une fiche de dépenses """
#         family_article = self.get_object()
#         user_qs = request.infoUser.get('id')
#         family_article.restore_family_article(user=user_qs, family_article_id = pk)
#         family_article = self.get_object()
#         return Response(
#             DenominationListingSerializer(
#                 family_article,
#                 context={"request": request, "family_article": family_article}
#             ).data,
#             status=status.HTTP_200_OK
#         )

# class CurrencyViewSet(viewsets.ModelViewSet):
#     queryset = Currency.objects.all()
#     serializer_class = CurrencySerializer

# class CashRegisterViewSet(viewsets.ModelViewSet):
#     queryset = CashRegister.objects.all()
#     serializer_class = CashRegisterSerializer  