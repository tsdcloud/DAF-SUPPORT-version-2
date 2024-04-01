from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from common.models import BaseUUIDModel
import http.client
import json
from common.middleware import generate_unique_num_ref
from django.core.mail import send_mail, send_mass_mail
from datetime import datetime

from django.db import DatabaseError, transaction
# from common.constances import H_OPERATION_CHOICE
from common.constances import H_OPERATION_CHOICE,StatutAvailabilityRequest, TYpeProduit,ENDPOINT_ENTITY, ENDPOINT_USER

from rest_framework.response import Response
from rest_framework import status
# from .models import AvailabilityRequest

# def generate_unique_num_ref():
#     # NUM_REF peut être défini dynamiquement ou statiquement en fonction de vos besoins
#     NUM_REF = 10001
#     # Obtenez le mois/année actuel au format MM/YYYY
#     codefin = datetime.now().strftime("%m/%Y")
#     # Comptez le nombre d'objets avec une num_ref se terminant par le codefin actuel
#     count = AvailabilityRequest.objects.filter(num_ref__endswith=codefin).count()
#     # Calculez le nouvel ID en ajoutant le nombre d'objets actuels à NUM_REF
#     new_id = NUM_REF + count
#     # Concaténez le nouvel ID avec le codefin pour former la nouvelle num_ref
#     concatenated_num_ref = f"{new_id}/{codefin}"
#     # concatenated_num_ref = str(new_id) + "/" + str(codefin) #f"{new_id}/{codefin}"
#     return concatenated_num_ref

# Create your models here.
class AvailabilityRequest(BaseUUIDModel):
    num_ref = models.CharField(max_length=255, unique=True)
    employer_initiateur = models.CharField(max_length=255)
    employer_controleur = models.CharField(max_length=255)
    employer_ordonnateur = models.CharField(max_length=255)
    employer_compta_mat = models.CharField(max_length=255, null=True, blank=True)
    requesting_service = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    statut = models.CharField(
        max_length=255,
        choices=[(choice.value, choice.name) for choice in StatutAvailabilityRequest],
        default=StatutAvailabilityRequest.VALIDATION_CONTROLEUR.value
    )
    type_produit = models.CharField(
        max_length=255,
        choices=[(choice.value, choice.name) for choice in StatutAvailabilityRequest],
        default=TYpeProduit.BIEN.value
    )
    num_dossier = models.CharField(max_length=255, null=True, blank=True)
    observation_controleur = models.TextField(null=True, blank=True)
    observation_ordonnateur = models.TextField(null=True, blank=True)
    
    date_valid_controleur = models.DateTimeField(null=True, blank=True)
    date_valid_ordonnateur = models.DateTimeField(null=True, blank=True)
    date_valid_compta_mat = models.DateTimeField(null=True, blank=True)

    site = models.CharField(max_length=255)
    entite = models.CharField(max_length=255)

    # active = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    
    @classmethod
    def create_availability_request(cls, employer_controleur, 
                             employer_ordonnateur, requesting_service, 
                             type_produit, site, entite, user,description = None, num_dossier =None):
        """
        Crée une fiche de dépenses.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            AvailabilityRequest or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        availability_request = AvailabilityRequest()
        availability_request.employer_initiateur = user
        availability_request.employer_controleur = employer_controleur
        availability_request.employer_ordonnateur = employer_ordonnateur
        availability_request.requesting_service = requesting_service
        availability_request.type_produit = type_produit
        if description :
            availability_request.description = description.upper()
        if num_dossier :
            availability_request.num_dossier = num_dossier
        availability_request.site = site
        availability_request.entite = entite
        availability_request.num_ref = generate_unique_num_ref(AvailabilityRequest)
        # availability_request.num_ref = generate_unique_num_ref()

        try:
            with transaction.atomic():
                availability_request._change_reason = json.dumps({"reason": "CREATE",
                                                           "user": user})
                availability_request.save()
            return availability_request
        except DatabaseError as e:
            print(f"Error when creating the expense sheet : {e}")
            return None
        
    
    @classmethod
    def validate_availability_request(cls, availability_request_id, description, user):
        try:
            availability_request = cls.objects.get(id=availability_request_id)
        except cls.DoesNotExist:
            return Response({"detail": "Availability reque sheet not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user or not description:
            return Response({"detail": "Missing user or observation in request data"}, status=status.HTTP_400_BAD_REQUEST)

        if availability_request.employer_controleur == user and availability_request.statut == 'VALIDATION CONTROLEUR':
            # validation conformity
            availability_request.observation_controleur = description
            availability_request.statut = 'VALIDATION ORDONNATEUR'
            availability_request.date_valid_controleur = datetime.now()

        elif availability_request.employer_ordonnateur == user and availability_request.statut == 'VALIDATION ORDONNATEUR':
            # validation authorizing officer
            availability_request.observation_ordonnateur = description
            availability_request.statut = 'VALIDATION COMPTABLE MATIERE'
            availability_request.date_valid_ordonnateur = datetime.now()

        elif availability_request.employer_budgetaire == user and availability_request.statut == 'VALIDATION COMPTABLE MATIERE':
            # validation budgetary
            availability_request.statut = 'RECU'
            availability_request.date_valid_compta_mat = datetime.now()

        else:
            # availability_request = None
            return Response({"detail": "This action cannot be performed. Check user or expense status"}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                availability_request._change_reason = json.dumps({"reason": "VALIDATION ", "user": user})
                availability_request.save()

            return availability_request  # Return the updated availability_request object

        except DatabaseError as e:
            # availability_request = None
            print(f"Error while availability reque sheet: {e}")
            return None
          
        
    @classmethod
    def rejection_availability_request(cls, availability_request_id, description, user):
        try:
            availability_request = cls.objects.get(id=availability_request_id)
        except cls.DoesNotExist:
            return Response({"detail": "Availability reque not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user or not description:
            return Response({"detail": "Missing user or observation in request data"}, status=status.HTTP_400_BAD_REQUEST)

        if availability_request.employer_controleur == user and availability_request.statut == 'VALIDATION CONTROLEUR':
            # validation conformity
            availability_request.observation_controleur = description
            availability_request.statut = 'REJET CONTROLEUR'
            availability_request.date_valid_controleur = datetime.now()


        elif availability_request.employer_ordonnateur == user and availability_request.statut == 'VALIDATION ORDONNATEUR':
            # validation authorizing officer
            availability_request.observation_ordonnateur = description
            availability_request.statut = 'REJET ORDONNATEUR'
            availability_request.date_valid_ordonnateur = datetime.now()

        else:
            # availability_request = None
            return Response({"detail": "This action cannot be performed. Check user or availability request status"}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                availability_request._change_reason = json.dumps({"reason": "VALIDATION ", "user": user})
                availability_request.save()

            return availability_request  # Return the updated availability_request object

        except DatabaseError as e:
            # availability_request = None
            print(f"Error while updating the expense sheet: {e}")
            return None
        
        
    @classmethod
    def update_availability_request(cls, availability_request_id, employer_controleur, 
                                    employer_ordonnateur, requesting_service,type_produit, 
                                    site, entite, user,description = None, num_dossier =None):
        """
        Met à jour une fiche de dépenses avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        availability_request = AvailabilityRequest.objects.get(id=availability_request_id)
        if availability_request.statut != 'VALIDATION CONTROLEUR':
            return None
        # availability_request.employer_initiateur = employer_initiateur
        availability_request.employer_controleur = employer_controleur
        availability_request.employer_ordonnateur = employer_ordonnateur
        availability_request.requesting_service = requesting_service
        availability_request.type_produit = type_produit
        availability_request.description = description.upper()
        availability_request.num_dossier = num_dossier
        availability_request.site = site
        availability_request.entite = entite
        try:
            with transaction.atomic():
                availability_request._change_reason = json.dumps({"reason": "UPDATED",
                                                           "user": user})
                availability_request.save()
            return availability_request
        except DatabaseError as e:
            print(f"Error while updating the expense sheet : {e}")
            return None
        
        
    @classmethod
    def delete_availability_request(cls, user: str, availability_request_id: str):
        """ delete availability_request """
        
        try:
            with transaction.atomic():
                availability_request_instance = cls.objects.get(id = availability_request_id)  # Remplacez ... par votre logique pour récupérer l'objet AvailabilityRequest
                availability_request_instance.is_active = False
                availability_request_instance._change_reason = json.dumps({"reason": "DELETE", "user": user})
                availability_request_instance.save()

            return availability_request_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        
        
    @classmethod
    def restore_availability_request(cls, user: str, availability_request_id: str):
        """ Restore availability_request """
        
        try:
            with transaction.atomic():
                availability_request_instance = cls.objects.get(id = availability_request_id)  # Remplacez ... par votre logique pour récupérer l'objet AvailabilityRequest
                availability_request_instance.is_active = True
                availability_request_instance._change_reason = json.dumps({"reason": "RESTORE", "user": user})
                availability_request_instance.save()
                
            return availability_request_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        

    def __str__(self):
        return self.num_ref



# Create your models here.
class WordingAvailabilityRequest(BaseUUIDModel):
    num_ref = models.CharField(max_length=255, unique=True)
    availability_requestst_id = models.ForeignKey(AvailabilityRequest, on_delete=models.SET_NULL)
    beneficiary_id = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    qantity = models.IntegerField()
    motif = models.CharField(max_length=255)
    date_use_start = models.DateTimeField()
    quantity_rewind = models.DateTimeField(null=True, blank=True)
    
    @classmethod
    def create_wording_availability_request(cls,user, availability_requestst_id, 
                             beneficiary_id, designation,qantity, 
                             motif, date_use_start, quantity_rewind):
        """
        Crée une fiche de libellé de DMD.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            AvailabilityRequest or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        wording_availability_request = WordingAvailabilityRequest()
        wording_availability_request.availability_requestst_id = availability_requestst_id
        wording_availability_request.beneficiary_id = beneficiary_id
        wording_availability_request.designation = designation
        wording_availability_request.qantity = qantity
        wording_availability_request.motif = motif
        wording_availability_request.date_use_start = date_use_start
        wording_availability_request.quantity_rewind = quantity_rewind
        wording_availability_request.num_ref = generate_unique_num_ref(WordingAvailabilityRequest)
        # availability_request.num_ref = generate_unique_num_ref()

        try:
            with transaction.atomic():
                wording_availability_request._change_reason = json.dumps({"reason": "CREATE",
                                                           "user": user})
                wording_availability_request.save()
            return wording_availability_request
        except DatabaseError as e:
            print(f"Error when creating the expense sheet : {e}")
            return None
        
    @classmethod
    def update_wording_availability_request(cls, wording_availability_request_id, user, availability_requestst_id, 
                                            beneficiary_id, designation,qantity,num_ref, 
                                            motif, date_use_start, quantity_rewind):
        """
        Met à jour le libellé d'une DMD avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        wording_availability_request = WordingAvailabilityRequest.objects.get(id=wording_availability_request_id)
        wording_availability_request.availability_requestst_id = availability_requestst_id
        wording_availability_request.beneficiary_id = beneficiary_id
        wording_availability_request.designation = designation
        wording_availability_request.qantity = qantity
        wording_availability_request.motif = motif
        wording_availability_request.date_use_start = date_use_start
        wording_availability_request.quantity_rewind = quantity_rewind
        wording_availability_request.num_ref = num_ref
        try:
            with transaction.atomic():
                wording_availability_request._change_reason = json.dumps({"reason": "UPDATED",
                                                           "user": user})
                wording_availability_request.save()
            return wording_availability_request
        except DatabaseError as e:
            print(f"Error while updating the expense sheet : {e}")
            return None   

    def __str__(self):
        return self.num_ref

    

# Create Attachement Availability Reque here.
class AttachementAvailabilityRequest(BaseUUIDModel):
    num_ref = models.CharField(max_length=255, unique=True)
    availability_requestst_id = models.ForeignKey(AvailabilityRequest, on_delete=models.SET_NULL)
    filename = models.CharField(max_length=255)
    
    @classmethod
    def create_attachement_availability_request(cls,user, availability_requestst_id, 
                             filename):
        """
        Crée une pièce-jointes de DMD.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            AvailabilityRequest or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        attachement_availability_request = AttachementAvailabilityRequest()
        attachement_availability_request.availability_requestst_id = availability_requestst_id
        attachement_availability_request.filename = filename
        attachement_availability_request.num_ref = generate_unique_num_ref(WordingAvailabilityRequest)

        try:
            with transaction.atomic():
                attachement_availability_request._change_reason = json.dumps({"reason": "CREATE",
                                                           "user": user})
                attachement_availability_request.save()
            return attachement_availability_request
        except DatabaseError as e:
            print(f"Error when creating the expense sheet : {e}")
            return None
        
    @classmethod
    def update_attachement_availability_request(cls, attachement_availability_request_id, user, 
                                            availability_requestst_id, filename, num_ref):
        """
        Met à jour une pièce-jointes avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        wording_availability_request = WordingAvailabilityRequest.objects.get(id=attachement_availability_request_id)
        wording_availability_request.availability_requestst_id = availability_requestst_id
        wording_availability_request.filename = filename
        wording_availability_request.num_ref = num_ref
        try:
            with transaction.atomic():
                wording_availability_request._change_reason = json.dumps({"reason": "UPDATED",
                                                           "user": user})
                wording_availability_request.save()
            return wording_availability_request
        except DatabaseError as e:
            print(f"Error while updating the expense sheet : {e}")
            return None 
    
    
    def __str__(self):
        return self.num_ref
