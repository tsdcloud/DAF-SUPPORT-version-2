from django.db import models
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
from common.constances import H_OPERATION_CHOICE,Module, TransactionType, TransactionStatus, ENDPOINT_ENTITY, ENDPOINT_USER

from rest_framework.response import Response
from rest_framework import status

# Create your models here.
class CashTransaction(BaseUUIDModel):
    num_ref = models.CharField(max_length=255, unique=True)
    cashier_id = models.CharField(max_length=255)
    employer_initiateur = models.CharField(max_length=255)
    montant = models.FloatField()
    
    transaction_type = models.CharField(
        max_length=255,
        choices=[(choice.value, choice.name) for choice in TransactionType]
    )
    module = models.CharField(
        max_length=255,
        choices=[(choice.value, choice.name) for choice in Module]
    )
    status = models.CharField(
        max_length=255,
        choices=[(choice.value, choice.name) for choice in TransactionStatus],
        default=TransactionStatus.NOT_EXECUTED.value
    )
    item_id = models.CharField(max_length=255)
    num_dossier = models.CharField(max_length=255, null=True, blank=True)
    
    employer_beneficiaire = models.CharField(max_length=255, null=True)
    date_valid_beneficiaire = models.DateTimeField(null=True, blank=True)
    code_validation = models.IntegerField(max_length=4, null=True, blank=True)
    

    site = models.CharField(max_length=255)
    entite = models.CharField(max_length=255)

    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    
    @classmethod
    def create_cash_transaction(cls, cashier_id, montant, transaction_type,
                             module, item_id, site, entite, user, 
                             num_dossier =None):
        """
        Crée une transaction de caisse.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            CashTransaction or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        cash_transaction = CashTransaction()
        cash_transaction.cashier_id = cashier_id
        cash_transaction.employer_initiateur = user
        cash_transaction.montant = montant
        cash_transaction.transaction_type = transaction_type
        cash_transaction.module = module
        cash_transaction.item_id = item_id
        if num_dossier :
            cash_transaction.num_dossier = num_dossier
        cash_transaction.site = site
        cash_transaction.entite = entite
        cash_transaction.num_ref = generate_unique_num_ref(CashTransaction)
 
        try:
            with transaction.atomic():
                cash_transaction._change_reason = json.dumps({"reason": "CREATE",
                                                           "user": user})
                cash_transaction.save()
            return cash_transaction
        except DatabaseError as e:
            print(f"Error when creating the expense sheet : {e}")
            return None
        
    
    @classmethod
    def validate_cash_transaction(cls, cash_transaction_id, description, user):
        try:
            cash_transaction = cls.objects.get(id=cash_transaction_id)
        except cls.DoesNotExist:
            return Response({"detail": "Availability reque sheet not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user or not description:
            return Response({"detail": "Missing user or observation in request data"}, status=status.HTTP_400_BAD_REQUEST)

        if cash_transaction.employer_controleur == user and cash_transaction.statut == 'VALIDATION CONTROLEUR':
            # validation conformity
            cash_transaction.observation_controleur = description
            cash_transaction.statut = 'VALIDATION ORDONNATEUR'
            cash_transaction.date_valid_controleur = datetime.now()

        elif cash_transaction.employer_ordonnateur == user and cash_transaction.statut == 'VALIDATION ORDONNATEUR':
            # validation authorizing officer
            cash_transaction.observation_ordonnateur = description
            cash_transaction.statut = 'VALIDATION COMPTABLE MATIERE'
            cash_transaction.date_valid_ordonnateur = datetime.now()

        elif cash_transaction.employer_budgetaire == user and cash_transaction.statut == 'VALIDATION COMPTABLE MATIERE':
            # validation budgetary
            cash_transaction.statut = 'RECU'
            cash_transaction.date_valid_compta_mat = datetime.now()

        else:
            # cash_transaction = None
            return Response({"detail": "This action cannot be performed. Check user or expense status"}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                cash_transaction._change_reason = json.dumps({"reason": "VALIDATION ", "user": user})
                cash_transaction.save()

            return cash_transaction  # Return the updated cash_transaction object

        except DatabaseError as e:
            # cash_transaction = None
            print(f"Error while availability reque sheet: {e}")
            return None
          
        
    @classmethod
    def rejection_cash_transaction(cls, cash_transaction_id, description, user):
        try:
            cash_transaction = cls.objects.get(id=cash_transaction_id)
        except cls.DoesNotExist:
            return Response({"detail": "Availability reque not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user or not description:
            return Response({"detail": "Missing user or observation in request data"}, status=status.HTTP_400_BAD_REQUEST)

        if cash_transaction.employer_controleur == user and cash_transaction.statut == 'VALIDATION CONTROLEUR':
            # validation conformity
            cash_transaction.observation_controleur = description
            cash_transaction.statut = 'REJET CONTROLEUR'
            cash_transaction.date_valid_controleur = datetime.now()


        elif cash_transaction.employer_ordonnateur == user and cash_transaction.statut == 'VALIDATION ORDONNATEUR':
            # validation authorizing officer
            cash_transaction.observation_ordonnateur = description
            cash_transaction.statut = 'REJET ORDONNATEUR'
            cash_transaction.date_valid_ordonnateur = datetime.now()

        else:
            # cash_transaction = None
            return Response({"detail": "This action cannot be performed. Check user or availability request status"}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                cash_transaction._change_reason = json.dumps({"reason": "VALIDATION ", "user": user})
                cash_transaction.save()

            return cash_transaction  # Return the updated cash_transaction object

        except DatabaseError as e:
            # cash_transaction = None
            print(f"Error while updating the expense sheet: {e}")
            return None
        
        
    @classmethod
    def update_cash_transaction(cls, cash_transaction_id, employer_controleur, 
                                    employer_ordonnateur, requesting_service,type_produit, 
                                    site, entite, user,description = None, num_dossier =None):
        """
        Met à jour une fiche de dépenses avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        cash_transaction = CashTransaction.objects.get(id=cash_transaction_id)
        if cash_transaction.statut != 'VALIDATION CONTROLEUR':
            return None
        # cash_transaction.employer_initiateur = employer_initiateur
        cash_transaction.employer_controleur = employer_controleur
        cash_transaction.employer_ordonnateur = employer_ordonnateur
        cash_transaction.requesting_service = requesting_service
        cash_transaction.type_produit = type_produit
        cash_transaction.description = description.upper()
        cash_transaction.num_dossier = num_dossier
        cash_transaction.site = site
        cash_transaction.entite = entite
        try:
            with transaction.atomic():
                cash_transaction._change_reason = json.dumps({"reason": "UPDATED",
                                                           "user": user})
                cash_transaction.save()
            return cash_transaction
        except DatabaseError as e:
            print(f"Error while updating the expense sheet : {e}")
            return None
        
        
    @classmethod
    def delete_cash_transaction(cls, user: str, cash_transaction_id: str):
        """ delete cash_transaction """
        
        try:
            with transaction.atomic():
                cash_transaction_instance = cls.objects.get(id = cash_transaction_id)  # Remplacez ... par votre logique pour récupérer l'objet CashTransaction
                cash_transaction_instance.is_active = False
                cash_transaction_instance._change_reason = json.dumps({"reason": "DELETE", "user": user})
                cash_transaction_instance.save()

            return cash_transaction_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        
        
    @classmethod
    def restore_cash_transaction(cls, user: str, cash_transaction_id: str):
        """ Restore cash_transaction """
        
        try:
            with transaction.atomic():
                cash_transaction_instance = cls.objects.get(id = cash_transaction_id)  # Remplacez ... par votre logique pour récupérer l'objet CashTransaction
                cash_transaction_instance.is_active = True
                cash_transaction_instance._change_reason = json.dumps({"reason": "RESTORE", "user": user})
                cash_transaction_instance.save()
                
            return cash_transaction_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        

    def __str__(self):
        return self.num_ref



# Create your models here.
class CashState(BaseUUIDModel):
    num_ref = models.CharField(max_length=255, unique=True)
    cash_transactionst_id = models.ForeignKey(CashTransaction, on_delete=models.SET_NULL, null=True)
    beneficiary_id = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    qantity = models.IntegerField()
    motif = models.CharField(max_length=255)
    date_use_start = models.DateTimeField()
    quantity_rewind = models.DateTimeField(null=True, blank=True)
    
    @classmethod
    def create_wording_cash_transaction(cls,user, cash_transactionst_id, 
                             beneficiary_id, designation,qantity, 
                             motif, date_use_start, quantity_rewind):
        """
        Crée une fiche de libellé de DMD.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            CashTransaction or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        wording_cash_transaction = WordingCashTransaction()
        wording_cash_transaction.cash_transactionst_id = cash_transactionst_id
        wording_cash_transaction.beneficiary_id = beneficiary_id
        wording_cash_transaction.designation = designation
        wording_cash_transaction.qantity = qantity
        wording_cash_transaction.motif = motif
        wording_cash_transaction.date_use_start = date_use_start
        wording_cash_transaction.quantity_rewind = quantity_rewind
        wording_cash_transaction.num_ref = generate_unique_num_ref(WordingCashTransaction)

        try:
            with transaction.atomic():
                wording_cash_transaction._change_reason = json.dumps({"reason": "CREATE",
                                                           "user": user})
                wording_cash_transaction.save()
            return wording_cash_transaction
        except DatabaseError as e:
            print(f"Error when creating the expense sheet : {e}")
            return None
        
    @classmethod
    def update_wording_cash_transaction(cls, wording_cash_transaction_id, user, cash_transactionst_id, 
                                            beneficiary_id, designation,qantity,num_ref, 
                                            motif, date_use_start, quantity_rewind):
        """
        Met à jour le libellé d'une DMD avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        wording_cash_transaction = WordingCashTransaction.objects.get(id=wording_cash_transaction_id)
        wording_cash_transaction.cash_transactionst_id = cash_transactionst_id
        wording_cash_transaction.beneficiary_id = beneficiary_id
        wording_cash_transaction.designation = designation
        wording_cash_transaction.qantity = qantity
        wording_cash_transaction.motif = motif
        wording_cash_transaction.date_use_start = date_use_start
        wording_cash_transaction.quantity_rewind = quantity_rewind
        wording_cash_transaction.num_ref = num_ref
        try:
            with transaction.atomic():
                wording_cash_transaction._change_reason = json.dumps({"reason": "UPDATED",
                                                           "user": user})
                wording_cash_transaction.save()
            return wording_cash_transaction
        except DatabaseError as e:
            print(f"Error while updating the expense sheet : {e}")
            return None   

    @classmethod
    def delete_wording_cash_transaction(cls, user: str, wording_cash_transaction_id: str):
        """ delete cash_transaction """
        
        try:
            with transaction.atomic():
                cash_transaction_instance = cls.objects.get(id = wording_cash_transaction_id)  # Remplacez ... par votre logique pour récupérer l'objet CashTransaction
                cash_transaction_instance.is_active = False
                cash_transaction_instance._change_reason = json.dumps({"reason": "DELETE", "user": user})
                cash_transaction_instance.save()

            return cash_transaction_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        
        
    @classmethod
    def restore_wording_cash_transaction(cls, user: str, wording_cash_transaction_id: str):
        """ Restore cash_transaction """
        
        try:
            with transaction.atomic():
                cash_transaction_instance = cls.objects.get(id = wording_cash_transaction_id)  # Remplacez ... par votre logique pour récupérer l'objet CashTransaction
                cash_transaction_instance.is_active = True
                cash_transaction_instance._change_reason = json.dumps({"reason": "RESTORE", "user": user})
                cash_transaction_instance.save()
                
            return cash_transaction_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        
        
    def __str__(self):
        return self.num_ref

    

# Create Attachement Availability Reque here.
class AttachementCashTransaction(BaseUUIDModel):
    num_ref = models.CharField(max_length=255, unique=True)
    cash_transactionst_id = models.ForeignKey(CashTransaction, on_delete=models.SET_NULL, null=True)
    filename = models.CharField(max_length=255)
    
    @classmethod
    def create_attachement_cash_transaction(cls,user, cash_transactionst_id, 
                             filename):
        """
        Crée une pièce-jointes de DMD.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            CashTransaction or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        attachement_cash_transaction = AttachementCashTransaction()
        attachement_cash_transaction.cash_transactionst_id = cash_transactionst_id
        attachement_cash_transaction.filename = filename
        attachement_cash_transaction.num_ref = generate_unique_num_ref(WordingCashTransaction)

        try:
            with transaction.atomic():
                attachement_cash_transaction._change_reason = json.dumps({"reason": "CREATE",
                                                           "user": user})
                attachement_cash_transaction.save()
            return attachement_cash_transaction
        except DatabaseError as e:
            print(f"Error when creating the expense sheet : {e}")
            return None
        
    @classmethod
    def update_attachement_cash_transaction(cls, attachement_cash_transaction_id, user, 
                                            cash_transactionst_id, filename, num_ref):
        """
        Met à jour une pièce-jointes avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        wording_cash_transaction = WordingCashTransaction.objects.get(id=attachement_cash_transaction_id)
        wording_cash_transaction.cash_transactionst_id = cash_transactionst_id
        wording_cash_transaction.filename = filename
        wording_cash_transaction.num_ref = num_ref
        try:
            with transaction.atomic():
                wording_cash_transaction._change_reason = json.dumps({"reason": "UPDATED",
                                                           "user": user})
                wording_cash_transaction.save()
            return wording_cash_transaction
        except DatabaseError as e:
            print(f"Error while updating the expense sheet : {e}")
            return None 
    
    
    def __str__(self):
        return self.num_ref
