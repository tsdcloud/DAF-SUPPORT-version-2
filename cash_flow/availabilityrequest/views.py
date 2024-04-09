# availabilityrequest/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from common.middleware import get_email_addressee, send_email
from django.shortcuts import get_object_or_404, render

from django.db import DatabaseError, transaction
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework.decorators import action
from datetime import datetime

from availabilityrequest.models import AvailabilityRequest, WordingAvailabilityRequest
from availabilityrequest.serializers import (AvailabilityRequestSerializer, AvailabilityRequestCreateSerializer,
                                  AvailabilityRequestListingSerializer, AvailabilityRequestDetailSerializer,
                                  AvailabilityRequestValidationSerializer, AvailabilityRequestValidationCodeSerializer,
                                  WordingAvailabilityRequestCreateSerializer, WordingAvailabilityRequestListingSerializer,
                                  WordingAvailabilityRequestSerializer)
from common.permissions import IsDeactivate, IsActivate
from availabilityrequest .permissions import (IsAddAvailabilityRequest, IsChangeAvailabilityRequest,
                                   IsDestroyAvailabilityRequest, IsRestoreAvailabilityRequest,
                                   IsViewDetailAvailabilityRequest, IsViewAllAvailabilityRequest,
                                   IsValidateAvailabilityRequest, IsRejecteAvailabilityRequest,
                                   IsAddWordingAvailabilityRequest, IsViewAllWordingAvailabilityRequest,
                                   IsChangeWordingAvailabilityRequest, IsDestroyWordingAvailabilityRequest,
                                   IsRestoreWordingAvailabilityRequest)

class AvailabilityRequestViewSet(viewsets.ModelViewSet):
    # queryset = AvailabilityRequest.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return AvailabilityRequestCreateSerializer
        if self.action == 'list':
            return AvailabilityRequestListingSerializer
        if self.action == 'retrieve':
            return AvailabilityRequestDetailSerializer
        if self.action == 'update':
            return AvailabilityRequestCreateSerializer
        if self.action == 'partial_update':
            print("partial_update")
            return AvailabilityRequestValidationSerializer
        if self.action == 'code_validation':
            return AvailabilityRequestValidationCodeSerializer
        return AvailabilityRequestSerializer
    
    
    def get_permissions(self):
        """ define permissions """
        if self.action == 'create':
            self.permission_classes = [IsAddAvailabilityRequest]
        elif self.action == 'list':
            self.permission_classes = [IsViewAllAvailabilityRequest]
        elif self.action == 'retrieve':
            self.permission_classes = [IsViewDetailAvailabilityRequest]
        elif self.action == 'update':
            self.permission_classes = [IsChangeAvailabilityRequest]
        elif self.action in ['partial_update', "rejection"]:
            self.permission_classes = [IsValidateAvailabilityRequest]
        elif self.action == 'partial_update':
            self.permission_classes = [IsValidateAvailabilityRequest]
        elif self.action == 'rejection':
            self.permission_classes = [IsRejecteAvailabilityRequest]
        elif self.action == 'destroy':
            self.permission_classes = [IsDestroyAvailabilityRequest]
        elif self.action == 'restore':
            self.permission_classes = [IsRestoreAvailabilityRequest]
        else:
            self.permission_classes = [IsDeactivate]
            # self.permission_classes = [IsActivate]
        return super().get_permissions()
    
    
    def get_queryset(self):
        """ define queryset """
        # Remplacez votre code actuel à la ligne 65 dans views.py par le suivant
        if self.request.infoUser and 'member' in self.request.infoUser and 'is_superuser' in self.request.infoUser['member']:
            if self.request.infoUser['member']['is_superuser'] is True:
                queryset = AvailabilityRequest.objects.all()
            else:
                queryset = AvailabilityRequest.objects.filter(is_active=True)
        else:
            # Gérez le cas où self.request.infoUser est None ou ne contient pas les clés attendues
            queryset = AvailabilityRequest.objects.filter(is_active=True)
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
                    availability_request = AvailabilityRequest.create_availability_request(
                        employer_controleur=serializer.validated_data['employer_controleur'],
                        employer_ordonnateur=serializer.validated_data['employer_ordonnateur'],
                        requesting_service=serializer.validated_data['requesting_service'],
                        type_produit=serializer.validated_data['type_produit'],
                        description=serializer.validated_data['description'],
                        num_dossier=serializer.validated_data['num_dossier'],
                        site=serializer.validated_data['site'],
                        entite=serializer.validated_data['entite'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                availability_request = None

            headers = self.get_success_headers(serializer.data)
            # email
            # addressee = get_email_addressee(availability_request.employer_controleur)
            # addressee = serializer.validated_data['employer_controleur']
            # print(addressee)
            # addressee = get_email_addressee(addressee)
            # addressee = get_email_addressee(serializer.validated_data['employer_controleur'])
            # print(addressee)
            # input("jesuis ici")
            # addressee = [addressee]
            # send_email(
            #     subject = f"Creation de fiche de dépense numéro: {availability_request.num_ref}",
            #     message = f"L'employé {request.infoUser.get('last_name')} { request.infoUser.get('first_name')}  
            #                 une fiche importante qui nécessite votre validation. Pour procéder, veuillez suivre le lien http://bfclimited.com /{availability_request.id}.Merci" ,
            #     recipient_list = addressee
            # )
            return Response(
                AvailabilityRequestListingSerializer(availability_request).data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Erreur lors de la création de la DMD"},
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
                    
                    availability_request = AvailabilityRequest.update_availability_request(
                        availability_request_id = pk,
                        employer_controleur=serializer.validated_data['employer_controleur'],
                        employer_ordonnateur=serializer.validated_data['employer_ordonnateur'],
                        requesting_service=serializer.validated_data['requesting_service'],
                        description=serializer.validated_data['description'],
                        type_produit=serializer.validated_data['type_produit'],
                        num_dossier=serializer.validated_data['num_dossier'],
                        site=serializer.validated_data['site'],
                        entite=serializer.validated_data['entite'],
                        user=request.infoUser.get('id')
                    )
                    
            except DatabaseError:
                availability_request = None

            headers = self.get_success_headers(serializer.data)
            return Response(
                AvailabilityRequestDetailSerializer(availability_request).data,
                status=status.HTTP_200_OK,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Error when updating availability request the status must be different of VALIDATION CONTROLEUR or data are not consistent"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
    
    def partial_update(self, request, pk=None, *args, **kwargs):
        # Logique pour mettre à jour un objet complet
        serializer = self.get_serializer(data=self.request.data)
        
        if serializer.is_valid(raise_exception=True):
            try:
                with transaction.atomic():
                    availability_request = AvailabilityRequest.validate_availability_request(
                        availability_request_id=pk,
                        description=serializer.validated_data['description'],
                        priority=serializer.validated_data['priority'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError as e:
                print(f"Database error during update: {e}")
                availability_request = None

            if availability_request:
                availability_request = self.get_object()
                return Response(
                    # availability_request.data,
                    AvailabilityRequestDetailSerializer(availability_request).data,
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
        
        
    @action(detail=True, methods=['patch'])
    def rejection(self, request, pk=None, *args, **kwargs):
        # Logique pour mettre à jour un objet complet
        serializer = AvailabilityRequestValidationSerializer(data=self.request.data)
        
        if serializer.is_valid(raise_exception=True):
            try:
                with transaction.atomic():
                    availability_request = AvailabilityRequest.rejection_availability_request(
                        availability_request_id=pk,
                        description=serializer.validated_data['description'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError as e:
                print(f"Database error during update: {e}")
                availability_request = None

            if availability_request:
                availability_request = self.get_object()
                return Response(
                    AvailabilityRequestDetailSerializer(availability_request).data,
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
        AvailabilityRequest = self.get_object()
        user_qs = request.infoUser.get('id')
        AvailabilityRequest.delete_availability_request(user=user_qs, availability_request_id = pk)
        AvailabilityRequest = self.get_object()
        return Response(
            AvailabilityRequestDetailSerializer(
                AvailabilityRequest,
                context={"request": request, "AvailabilityRequest": AvailabilityRequest}
            ).data,
            status=status.HTTP_200_OK
        )
    
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None, ):
        """ Action pour restorer une fiche de dépenses """
        AvailabilityRequest = self.get_object()
        user_qs = request.infoUser.get('id')
        AvailabilityRequest.restore_availability_request(user=user_qs, availability_request_id = pk)
        AvailabilityRequest = self.get_object()
        return Response(
            AvailabilityRequestDetailSerializer(
                AvailabilityRequest,
                context={"request": request, "AvailabilityRequest": AvailabilityRequest}
            ).data,
            status=status.HTTP_200_OK
        )


class WordingAvailabilityRequestViewSet(viewsets.ModelViewSet):
    # queryset = FamilyWordingAvailabilityRequest.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return WordingAvailabilityRequestCreateSerializer
        if self.action == 'list':
            return WordingAvailabilityRequestListingSerializer
        if self.action == 'retrieve':
            return WordingAvailabilityRequestListingSerializer
        if self.action == 'update':
            return WordingAvailabilityRequestCreateSerializer
        return WordingAvailabilityRequestSerializer
    
    
    def get_permissions(self):
        """ define permissions """
        if self.action == 'create':
            self.permission_classes = [IsAddWordingAvailabilityRequest]
        elif self.action == 'list':
            self.permission_classes = [IsViewAllWordingAvailabilityRequest]
        elif self.action == 'retrieve':
            self.permission_classes = [IsViewAllWordingAvailabilityRequest]
        elif self.action == 'update':
            self.permission_classes = [IsChangeWordingAvailabilityRequest]
        elif self.action == 'destroy':
            self.permission_classes = [IsDestroyWordingAvailabilityRequest]
        elif self.action == 'restore':
            self.permission_classes = [IsRestoreWordingAvailabilityRequest]
        else:
            self.permission_classes = [IsDeactivate]
        return super().get_permissions()
    
    
    def get_queryset(self):
        """ define queryset """
        # Remplacez votre code actuel à la ligne 65 dans views.py par le suivant
        if self.request.infoUser and 'member' in self.request.infoUser and 'is_superuser' in self.request.infoUser['member']:
            if self.request.infoUser['member']['is_superuser'] is True:
                queryset = WordingAvailabilityRequest.objects.all()
            else:
                queryset = WordingAvailabilityRequest.objects.filter(is_active=True)
        else:
            # Gérez le cas où self.request.infoUser est None ou ne contient pas les clés attendues
            queryset = WordingAvailabilityRequest.objects.filter(is_active=True)
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
                    wording_availability_request = WordingAvailabilityRequest.create_WordingAvailabilityRequest(
                        wording_availability_request_id=serializer.validated_data['wording_availability_request_id'],
                        label=serializer.validated_data['label'],
                        sigle=serializer.validated_data['sigle'],
                        description=serializer.validated_data['description'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                wording_availability_request = None

            headers = self.get_success_headers(serializer.data)
            
            return Response(
                WordingAvailabilityRequestListingSerializer(wording_availability_request).data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Erreur lors de la création de la famille d'WordingAvailabilityRequest"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
              
    
    def list(self, request, *args, **kwargs):
        """
        This view intends to render all WordingAvailabilityRequest.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        
        queryset = self.get_queryset()
            
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
                    wording_availability_request = WordingAvailabilityRequest.update_WordingAvailabilityRequest(
                        cls = self,
                        WordingAvailabilityRequest_id = pk,
                        wording_availability_request_id=serializer.validated_data['wording_availability_request_id'],
                        label=serializer.validated_data['label'],
                        sigle=serializer.validated_data['sigle'],
                        description=serializer.validated_data['description'],
                        user=request.infoUser.get('id')
                    )
            except DatabaseError:
                wording_availability_request = None

            headers = self.get_success_headers(serializer.data)
            return Response(
                WordingAvailabilityRequestListingSerializer(wording_availability_request).data,
                status=status.HTTP_200_OK,
                headers=headers
            )
        else:
            return Response(
                {"detail": "Error when updated wording availability request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
    def destroy(self, request, pk=None):
        """ Action pour supprimer un libellé de DMD """
        wording_availability_request = self.get_object()
        user_qs = request.infoUser.get('id')
        wording_availability_request.delete_wording_availability_request(user=user_qs, WordingAvailabilityRequest_id = pk)
        wording_availability_request = self.get_object()
        return Response(
            WordingAvailabilityRequestListingSerializer(
                wording_availability_request,
                context={"request": request, "wording_availability_request": WordingAvailabilityRequest}
            ).data,
            status=status.HTTP_200_OK
        )
        
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None, ):
        """ Action pour restorer un libelleé de DMD """
        wording_availability_request = self.get_object()
        user_qs = request.infoUser.get('id')
        wording_availability_request.restore_wording_availability_request(user=user_qs, WordingAvailabilityRequest_id = pk)
        wording_availability_request = self.get_object()
        return Response(
            WordingAvailabilityRequestListingSerializer(
                WordingAvailabilityRequest,
                context={"request": request, "wording_availability_request": WordingAvailabilityRequest}
            ).data,
            status=status.HTTP_200_OK
        )   
