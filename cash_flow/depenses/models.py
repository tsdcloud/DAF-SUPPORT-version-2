from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from common.models import BaseUUIDModel
import http.client
import json
from django.core.mail import send_mail, send_mass_mail
from datetime import datetime

from django.db import DatabaseError, transaction
from common.constances import ENDPOINT_ENTITY, ENDPOINT_USER,H_OPERATION_CHOICE,StatutExpenseSheet, StatutReturnToCashier
from common.middleware import generate_unique_num_ref

from rest_framework.response import Response
from rest_framework import status
# from .models import ExpenseSheet

# def generate_unique_num_ref():
#     # NUM_REF peut être défini dynamiquement ou statiquement en fonction de vos besoins
#     NUM_REF = 10001
#     # Obtenez le mois/année actuel au format MM/YYYY
#     codefin = datetime.now().strftime("%m/%Y")
#     # Comptez le nombre d'objets avec une num_ref se terminant par le codefin actuel
#     count = ExpenseSheet.objects.filter(num_ref__endswith=codefin).count()
#     # Calculez le nouvel ID en ajoutant le nombre d'objets actuels à NUM_REF
#     new_id = NUM_REF + count
#     # Concaténez le nouvel ID avec le codefin pour former la nouvelle num_ref
#     concatenated_num_ref = f"{new_id}/{codefin}"
#     # concatenated_num_ref = str(new_id) + "/" + str(codefin) #f"{new_id}/{codefin}"
#     return concatenated_num_ref
    

          
class ExpenseSheet(BaseUUIDModel):
    employer_initiateur = models.CharField(max_length=255)
    employer_beneficiaire = models.CharField(max_length=255)
    employer_conformite = models.CharField(max_length=255)
    employer_budgetaire = models.CharField(max_length=255)
    employer_ordonnateur = models.CharField(max_length=255)
    employer_caissier = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    montant = models.FloatField()
    num_ref = models.CharField(max_length=255, unique=True)
    num_dossier = models.CharField(max_length=255, null=True, blank=True)

    statut = models.CharField(
        max_length=255,
        choices=[(choice.value, choice.name) for choice in StatutExpenseSheet],
        default=StatutExpenseSheet.VALIDATION_CONFORMITE.value
    )
    observation_conformite = models.TextField(null=True, blank=True)
    observation_budgetaire = models.TextField(null=True, blank=True)
    observation_ordonnateur = models.TextField(null=True, blank=True)

    date_init = models.DateTimeField(auto_now_add=True)
    date_valid_conformite = models.DateTimeField(null=True, blank=True)
    date_valid_budgetaire = models.DateTimeField(null=True, blank=True)
    date_valid_ordonnateur = models.DateTimeField(null=True, blank=True)
    date_valid_decaissement = models.DateTimeField(null=True, blank=True)

    site = models.CharField(max_length=255)
    entite = models.CharField(max_length=255)
    code_validation = models.CharField(max_length=255, null=True, blank=True)
    expiration_time = models.DateTimeField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    
    @classmethod
    def create_expense_sheet(cls, employer_beneficiaire, employer_conformite, 
                             employer_budgetaire, employer_ordonnateur, description, 
                             montant, site, entite, user,num_dossier = None):
        """
        Crée une fiche de dépenses.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            ExpenseSheet or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        expense_sheet = ExpenseSheet()
        expense_sheet.employer_initiateur = user
        expense_sheet.employer_beneficiaire = employer_beneficiaire
        expense_sheet.employer_conformite = employer_conformite
        expense_sheet.employer_budgetaire = employer_budgetaire
        expense_sheet.employer_ordonnateur = employer_ordonnateur
        expense_sheet.description = description.upper()
        expense_sheet.montant = montant
        expense_sheet.site = site
        expense_sheet.entite = entite
        # expense_sheet.num_ref = generate_unique_num_ref()
        expense_sheet.num_ref = generate_unique_num_ref(ExpenseSheet)
        if num_dossier:
            expense_sheet.num_dossier = num_dossier

        try:
            with transaction.atomic():
                expense_sheet._change_reason = json.dumps({"reason": "CREATE",
                                                           "user": user})
                expense_sheet.save()
            return expense_sheet
        except DatabaseError as e:
            print(f"Error when creating the expense sheet : {e}")
            return None
        
    
    @classmethod
    def validate_expense_sheet(cls, expense_sheet_id, observation, user):
        try:
            expense_sheet = cls.objects.get(id=expense_sheet_id)
        except cls.DoesNotExist:
            return Response({"detail": "Expense sheet not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user or not observation:
            return Response({"detail": "Missing user or observation in request data"}, status=status.HTTP_400_BAD_REQUEST)

        if expense_sheet.employer_conformite == user and expense_sheet.statut == 'VALIDATION CONFORMITE':
            # validation conformity
            expense_sheet.observation_conformite = observation
            expense_sheet.statut = 'VALIDATION BUDGETAIRE'
            expense_sheet.date_valid_conformite = datetime.now()

        elif expense_sheet.employer_budgetaire == user and expense_sheet.statut == 'VALIDATION BUDGETAIRE':
            # validation budgetary
            expense_sheet.observation_budgetaire = observation
            expense_sheet.statut = 'VALIDATION ORDONNATEUR'
            expense_sheet.date_valid_budgetaire = datetime.now()

        elif expense_sheet.employer_ordonnateur == user and expense_sheet.statut == 'VALIDATION ORDONNATEUR':
            # validation authorizing officer
            expense_sheet.observation_ordonnateur = observation
            expense_sheet.statut = 'VALIDATION DECAISSEMENT'
            expense_sheet.date_valid_ordonnateur = datetime.now()

        else:
            # expense_sheet = None
            return Response({"detail": "This action cannot be performed. Check user or expense status"}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                expense_sheet._change_reason = json.dumps({"reason": "VALIDATION ", "user": user})
                expense_sheet.save()

            return expense_sheet  # Return the updated expense_sheet object

        except DatabaseError as e:
            # expense_sheet = None
            print(f"Error while updating the expense sheet: {e}")
            return None
          
        
    @classmethod
    def rejection_expense_sheet(cls, expense_sheet_id, observation, user):
        try:
            expense_sheet = cls.objects.get(id=expense_sheet_id)
        except cls.DoesNotExist:
            return Response({"detail": "Expense sheet not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user or not observation:
            return Response({"detail": "Missing user or observation in request data"}, status=status.HTTP_400_BAD_REQUEST)

        if expense_sheet.employer_conformite == user and expense_sheet.statut == 'VALIDATION CONFORMITE':
            # validation conformity
            expense_sheet.observation_conformite = observation
            expense_sheet.statut = 'REJET CONFORMITE'
            expense_sheet.date_valid_conformite = datetime.now()

        elif expense_sheet.employer_budgetaire == user and expense_sheet.statut == 'VALIDATION BUDGETAIRE':
            # validation budgetary
            expense_sheet.observation_budgetaire = observation
            expense_sheet.statut = 'REJET BUDGETAIRE'
            expense_sheet.date_valid_budgetaire = datetime.now()

        elif expense_sheet.employer_ordonnateur == user and expense_sheet.statut == 'VALIDATION ORDONNATEUR':
            # validation authorizing officer
            expense_sheet.observation_ordonnateur = observation
            expense_sheet.statut = 'REJET ORDONNATEUR'
            expense_sheet.date_valid_ordonnateur = datetime.now()

        else:
            # expense_sheet = None
            return Response({"detail": "This action cannot be performed. Check user or expense status"}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                expense_sheet._change_reason = json.dumps({"reason": "VALIDATION ", "user": user})
                expense_sheet.save()

            return expense_sheet  # Return the updated expense_sheet object

        except DatabaseError as e:
            # expense_sheet = None
            print(f"Error while updating the expense sheet: {e}")
            return None
        
        
    @classmethod
    def update_expense_sheet(cls, expense_sheet_id, employer_initiateur, employer_beneficiaire, employer_conformite, 
                             employer_budgetaire, employer_ordonnateur, description, num_dossier, num_ref, 
                             montant, site, entite, user):
        """
        Met à jour une fiche de dépenses avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        expense_sheet = ExpenseSheet.objects.get(id=expense_sheet_id)
        expense_sheet.employer_initiateur = employer_initiateur
        expense_sheet.employer_beneficiaire = employer_beneficiaire
        expense_sheet.employer_conformite = employer_conformite
        expense_sheet.employer_budgetaire = employer_budgetaire
        expense_sheet.employer_ordonnateur = employer_ordonnateur
        expense_sheet.description = description.upper()
        expense_sheet.montant = montant
        expense_sheet.num_dossier = num_dossier
        expense_sheet.site = site
        expense_sheet.entite = entite
        expense_sheet.num_ref = num_ref
        try:
            with transaction.atomic():
                expense_sheet._change_reason = json.dumps({"reason": "UPDATED",
                                                           "user": user})
                expense_sheet.save()
            return expense_sheet
        except DatabaseError as e:
            print(f"Error while updating the expense sheet : {e}")
            return None
        
        
    @classmethod
    def delete_expense_sheet(cls, user: str, expense_sheet_id: str):
        """ delete expense_sheet """
        
        try:
            with transaction.atomic():
                expense_sheet_instance = cls.objects.get(id = expense_sheet_id)  # Remplacez ... par votre logique pour récupérer l'objet ExpenseSheet
                expense_sheet_instance.is_active = False
                expense_sheet_instance._change_reason = json.dumps({"reason": "DELETE", "user": user})
                expense_sheet_instance.save()

            return expense_sheet_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        
        
    @classmethod
    def restore_expense_sheet(cls, user: str, expense_sheet_id: str):
        """ Restore expense_sheet """
        
        try:
            with transaction.atomic():
                expense_sheet_instance = cls.objects.get(id = expense_sheet_id)  # Remplacez ... par votre logique pour récupérer l'objet ExpenseSheet
                expense_sheet_instance.is_active = True
                expense_sheet_instance._change_reason = json.dumps({"reason": "RESTORE", "user": user})
                expense_sheet_instance.save()
                
            return expense_sheet_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        

    def __str__(self):
        return self.num_ref



class ReturnToCashier(BaseUUIDModel):
    employer_initiateur = models.CharField(max_length=255)
    remaining_amount = models.FloatField()
    expense_sheet_id = models.ForeignKey(ExpenseSheet, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    num_ref = models.CharField(max_length=255, unique=True)
    num_dossier = models.CharField(max_length=255, null=True, blank=True)
    statut = models.CharField(
        max_length=255,
        choices=[(choice.value, choice.name) for choice in StatutExpenseSheet],
        default=StatutReturnToCashier.VALIDATION_CAISSE.value
    )
    
    employer_conformite = models.CharField(max_length=255)
    employer_budgetaire = models.CharField(max_length=255)
    employer_ordonnateur = models.CharField(max_length=255)
    employer_caissier = models.CharField(max_length=255, null=True, blank=True)
    montant = models.FloatField()
    observation_conformite = models.TextField(null=True, blank=True)
    observation_budgetaire = models.TextField(null=True, blank=True)
    observation_ordonnateur = models.TextField(null=True, blank=True)

    date_init = models.DateTimeField(auto_now_add=True)
    date_valid_conformite = models.DateTimeField(null=True, blank=True)
    date_valid_budgetaire = models.DateTimeField(null=True, blank=True)
    date_valid_ordonnateur = models.DateTimeField(null=True, blank=True)
    date_valid_decaissement = models.DateTimeField(null=True, blank=True)

    site = models.CharField(max_length=255)
    entite = models.CharField(max_length=255)
    code_validation = models.CharField(max_length=255, null=True, blank=True)
    expiration_time = models.DateTimeField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)