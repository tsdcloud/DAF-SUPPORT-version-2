from django.db import models

from django.utils import timezone
from django.contrib.auth.models import User

from common.models import BaseUUIDModel
import http.client
import json
from django.core.mail import send_mail, send_mass_mail
from datetime import datetime

from django.db import DatabaseError, transaction
from common.constances import ENDPOINT_ENTITY, ENDPOINT_USER,H_OPERATION_CHOICE, StatutReturnToCashier, PaymentMethods
from common.middleware import generate_unique_num_ref

from rest_framework.response import Response
from rest_framework import status
from depenses.models import ExpenseSheet

          
class ReturnToCashier(BaseUUIDModel):
    employer_initiateur = models.CharField(max_length=255)
    remaining_balance = models.FloatField()
    expense_sheet_id = models.ForeignKey(ExpenseSheet, on_delete=models.PROTECT) 
    description = models.TextField()
    num_dossier = models.CharField(max_length=255, null=True, blank=True)
    statut = models.CharField(
        max_length=255,
        choices=[(choice.value, choice.name) for choice in StatutReturnToCashier],
        default=StatutReturnToCashier.INITIE.value
    )
    payment_method = models.CharField(
        max_length=255,
        choices=[(choice.value, choice.name) for choice in PaymentMethods],
        default=PaymentMethods.ESPECES.value
    )
    num_ref = models.CharField(max_length=255, unique=True)

    site = models.CharField(max_length=255)
    entite = models.CharField(max_length=255)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    
    @classmethod
    def create_return_to_cashier(cls, expense_sheet_id, remaining_balance,
                             description, payment_method,
                             site, entite, user,num_dossier = None):
        """
        Crée une fiche de dépenses.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            ReturnToCashier or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        return_to_cashier = ReturnToCashier()
        return_to_cashier.employer_initiateur = user
        return_to_cashier.expense_sheet_id = expense_sheet_id
        return_to_cashier.remaining_balance = remaining_balance
        return_to_cashier.description = description.upper()
        return_to_cashier.payment_method = payment_method
        return_to_cashier.site = site
        return_to_cashier.entite = entite
        return_to_cashier.num_ref = generate_unique_num_ref(ReturnToCashier)
        if num_dossier:
            return_to_cashier.num_dossier = num_dossier

        try:
            with transaction.atomic():
                return_to_cashier._change_reason = json.dumps({"reason": "CREATE",
                                                           "user": user})
                return_to_cashier.save()
            return return_to_cashier
        except DatabaseError as e:
            print(f"Error when creating the expense sheet : {e}")
            return None
        
    
    @classmethod
    def validate_return_to_cashier(cls, return_to_cashier_id, observation, user):
        try:
            return_to_cashier = cls.objects.get(id=return_to_cashier_id)
        except cls.DoesNotExist:
            return Response({"detail": "Expense sheet not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user or not observation:
            return Response({"detail": "Missing user or observation in request data"}, status=status.HTTP_400_BAD_REQUEST)

        if return_to_cashier.employer_conformite == user and return_to_cashier.statut == 'VALIDATION CONFORMITE':
            # validation conformity
            return_to_cashier.observation_conformite = observation
            return_to_cashier.statut = 'VALIDATION BUDGETAIRE'
            return_to_cashier.date_valid_conformite = datetime.now()

        elif return_to_cashier.employer_budgetaire == user and return_to_cashier.statut == 'VALIDATION BUDGETAIRE':
            # validation budgetary
            return_to_cashier.observation_budgetaire = observation
            return_to_cashier.statut = 'VALIDATION ORDONNATEUR'
            return_to_cashier.date_valid_budgetaire = datetime.now()

        elif return_to_cashier.employer_ordonnateur == user and return_to_cashier.statut == 'VALIDATION ORDONNATEUR':
            # validation authorizing officer
            return_to_cashier.observation_ordonnateur = observation
            return_to_cashier.statut = 'VALIDATION DECAISSEMENT'
            return_to_cashier.date_valid_ordonnateur = datetime.now()

        else:
            # return_to_cashier = None
            return Response({"detail": "This action cannot be performed. Check user or expense status"}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                return_to_cashier._change_reason = json.dumps({"reason": "VALIDATION ", "user": user})
                return_to_cashier.save()

            return return_to_cashier  # Return the updated return_to_cashier object

        except DatabaseError as e:
            # return_to_cashier = None
            print(f"Error while updating the expense sheet: {e}")
            return None
          
        
    @classmethod
    def rejection_return_to_cashier(cls, return_to_cashier_id, observation, user):
        try:
            return_to_cashier = cls.objects.get(id=return_to_cashier_id)
        except cls.DoesNotExist:
            return Response({"detail": "Expense sheet not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user or not observation:
            return Response({"detail": "Missing user or observation in request data"}, status=status.HTTP_400_BAD_REQUEST)

        if return_to_cashier.employer_conformite == user and return_to_cashier.statut == 'VALIDATION CONFORMITE':
            # validation conformity
            return_to_cashier.observation_conformite = observation
            return_to_cashier.statut = 'REJET CONFORMITE'
            return_to_cashier.date_valid_conformite = datetime.now()

        elif return_to_cashier.employer_budgetaire == user and return_to_cashier.statut == 'VALIDATION BUDGETAIRE':
            # validation budgetary
            return_to_cashier.observation_budgetaire = observation
            return_to_cashier.statut = 'REJET BUDGETAIRE'
            return_to_cashier.date_valid_budgetaire = datetime.now()

        elif return_to_cashier.employer_ordonnateur == user and return_to_cashier.statut == 'VALIDATION ORDONNATEUR':
            # validation authorizing officer
            return_to_cashier.observation_ordonnateur = observation
            return_to_cashier.statut = 'REJET ORDONNATEUR'
            return_to_cashier.date_valid_ordonnateur = datetime.now()

        else:
            # return_to_cashier = None
            return Response({"detail": "This action cannot be performed. Check user or expense status"}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                return_to_cashier._change_reason = json.dumps({"reason": "VALIDATION ", "user": user})
                return_to_cashier.save()

            return return_to_cashier  # Return the updated return_to_cashier object

        except DatabaseError as e:
            # return_to_cashier = None
            print(f"Error while updating the expense sheet: {e}")
            return None
        
        
    @classmethod
    def update_return_to_cashier(cls, return_to_cashier_id, expense_sheet_id, remaining_balance,
                             description, payment_method,
                             site, entite, user,num_dossier = None):
        """
        Met à jour une fiche de dépenses avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        return_to_cashier = ReturnToCashier.objects.get(id=return_to_cashier_id)
        return_to_cashier.employer_initiateur = user
        return_to_cashier.expense_sheet_id = expense_sheet_id
        return_to_cashier.remaining_balance = remaining_balance
        return_to_cashier.description = description.upper()
        return_to_cashier.payment_method = payment_method
        return_to_cashier.site = site
        return_to_cashier.entite = entite
        if num_dossier:
            return_to_cashier.num_dossier = num_dossier
        try:
            with transaction.atomic():
                return_to_cashier._change_reason = json.dumps({"reason": "UPDATED",
                                                           "user": user})
                return_to_cashier.save()
            return return_to_cashier
        except DatabaseError as e:
            print(f"Error while updating the expense sheet : {e}")
            return None
        
        
    @classmethod
    def delete_return_to_cashier(cls, user: str, return_to_cashier_id: str):
        """ delete return_to_cashier """
        
        try:
            with transaction.atomic():
                return_to_cashier_instance = cls.objects.get(id = return_to_cashier_id)  # Remplacez ... par votre logique pour récupérer l'objet ReturnToCashier
                return_to_cashier_instance.is_active = False
                return_to_cashier_instance._change_reason = json.dumps({"reason": "DELETE", "user": user})
                return_to_cashier_instance.save()

            return return_to_cashier_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        
        
    @classmethod
    def restore_return_to_cashier(cls, user: str, return_to_cashier_id: str):
        """ Restore return_to_cashier """
        
        try:
            with transaction.atomic():
                return_to_cashier_instance = cls.objects.get(id = return_to_cashier_id)  # Remplacez ... par votre logique pour récupérer l'objet ReturnToCashier
                return_to_cashier_instance.is_active = True
                return_to_cashier_instance._change_reason = json.dumps({"reason": "RESTORE", "user": user})
                return_to_cashier_instance.save()
                
            return return_to_cashier_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        

    @classmethod
    def execute_return_to_cashier(cls, return_to_cashier_id, user):
        """
        Met à jour une fiche de dépenses avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        return_to_cashier = ReturnToCashier.objects.get(id=return_to_cashier_id)
        return_to_cashier.statut = 'EXECUTE'
        try:
            with transaction.atomic():
                return_to_cashier._change_reason = json.dumps({"reason": "EXECUTION",
                                                        "user": user})
                return_to_cashier.save()
            return return_to_cashier
        except DatabaseError as e:
            print(f"Error while execution the expense sheet : {e}")
            return None
        
    @classmethod
    def check_return_to_cashier(cls, return_to_cashier_id):
        try:
            return_to_cashier = cls.objects.get(id=return_to_cashier_id)
            return True
        except cls.DoesNotExist:
            return False
        
        
    def __str__(self):
        return self.num_ref


