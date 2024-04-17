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
from common.constances import H_OPERATION_CHOICE,Module, TransactionType, TransactionStatus, ENDPOINT_ENTITY, ENDPOINT_USER,TypeCashRegisterAction

from rest_framework.response import Response
from rest_framework import status
from depenses.models import ExpenseSheet

# Create your models here.
class CashTransaction(BaseUUIDModel):
    employer_initiateur = models.CharField(max_length=255)
    cashier_id = models.CharField(max_length=255)
    num_ref = models.CharField(max_length=255, unique=True)
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
    description = models.TextField()
    
    code_validation = models.CharField(null=True, max_length=4, blank=True)
    expiration_time = models.DateTimeField(null=True, blank=True)

    site = models.CharField(max_length=255)
    entite = models.CharField(max_length=255)

    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    
    @classmethod
    def is_valid_code(cls, expiration_time):
        # Vérifie si expiration_time est défini
        if expiration_time:
            # Compare l'heure actuelle avec expiration_time
            return timezone.now() <= expiration_time
        else:
            # Si expiration_time n'est pas défini, il n'est pas expiré
            return False
    
    @classmethod
    def create_cash_transaction(cls, cashier_id, montant, employer_beneficiaire,
                             transaction_type, module, item_id, site, entite, user, 
                             description,num_dossier =None):
        """
        Crée une transaction de caisse.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            CashTransaction or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        cash_transaction = CashTransaction()
        cash_transaction.employer_initiateur = user
        cash_transaction.employer_beneficiaire = employer_beneficiaire
        cash_transaction.cashier_id = cashier_id
        cash_transaction.montant = montant
        cash_transaction.transaction_type = transaction_type
        cash_transaction.module = module
        cash_transaction.item_id = item_id
        cash_transaction.description = description.upper()
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
    def generate_code_cash_transaction(cls, cash_transaction_id, code_validation, expiration_time, user):
        try:
            cash_transaction = cls.objects.get(id=cash_transaction_id)
        except cls.DoesNotExist:
            return Response({"detail": "Availability reque sheet not found"}, status=status.HTTP_404_NOT_FOUND)

      
        cash_transaction.code_validation = code_validation
        cash_transaction.expiration_time = expiration_time

        try:
            with transaction.atomic():
                cash_transaction._change_reason = json.dumps({"reason": "GENERATION_CODE_VALIDATION ", "user": user})
                cash_transaction.save()

            return cash_transaction  # Return the updated cash_transaction object

        except DatabaseError as e:
            # cash_transaction = None
            print(f"Error while cash transaction reque sheet: {e}")
            return None
        
        
    @classmethod
    def validate_cash_transaction(cls, cash_transaction_id, code_validation, user):
        try:
            cash_transaction = cls.objects.get(id=cash_transaction_id)
        except cls.DoesNotExist:
            return Response({"detail": "Availability reque sheet not found"}, status=status.HTTP_404_NOT_FOUND)
        
        expiration_time = cash_transaction.expiration_time
        print(cash_transaction.is_valid_code(expiration_time))
        if (cash_transaction.is_valid_code(expiration_time) and
            cash_transaction.status == 'NOT EXECUTED' and
            cash_transaction.code_validation == code_validation):
    
            try:
                with transaction.atomic():
                    # validation beneficiaire
                    cash_transaction.status = 'EXECUTED'
                    cash_transaction.date_valid_beneficiaire = datetime.now()
                    if cash_transaction.module == 'DEPENSE':
                        ExpenseSheet.execute_expense_sheet(expense_sheet_id=cash_transaction.item_id,
                                                        user = user)
                    elif cash_transaction.module == 'RECETTE':
                        pass
                    elif cash_transaction.module == 'RETOUR CAISSE':
                        pass
                    elif cash_transaction.module == 'APPROVISIONNEMENT CAISSE':
                        pass
                    cash_transaction._change_reason = json.dumps({"reason": "VALIDATION ", "user": user})
                    cash_transaction.save()

                return cash_transaction  # Return the updated cash_transaction object

            except DatabaseError as e:
                # cash_transaction = None
                print(f"Error while availability reque sheet: {e}")
                return None        
        else:
            print("false en validation")
            # cash_transaction = None
            return None
            # return Response({"detail": "This action cannot be performed. Check user or expense status"}, status=status.HTTP_403_FORBIDDEN)

          
          
    @classmethod
    def update_cash_transaction(cls, cash_transaction_id, cashier_id, montant, employer_beneficiaire,
                             transaction_type, module, item_id, site, entite, user, 
                             description,num_dossier =None):
        """
        Met à jour une fiche de dépenses avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        cash_transaction = CashTransaction.objects.get(id=cash_transaction_id)
        if cash_transaction.statut != 'EXECUTED':
            return Response({"detail": "This action cannot be performed. Check user or Cash Transaction status"}, status=status.HTTP_403_FORBIDDEN)
        
        cash_transaction.employer_initiateur = user
        cash_transaction.employer_beneficiaire = employer_beneficiaire
        cash_transaction.cashier_id = cashier_id
        cash_transaction.montant = montant
        cash_transaction.transaction_type = transaction_type
        cash_transaction.module = module
        cash_transaction.item_id = item_id
        cash_transaction.description = description.upper()
        if num_dossier :
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
# class CashState(BaseUUIDModel):
#     num_ref = models.CharField(max_length=255, unique=True)
#     cash_transactionst_id = models.ForeignKey(CashTransaction, on_delete=models.SET_NULL, null=True)
#     beneficiary_id = models.CharField(max_length=255)
#     designation = models.CharField(max_length=255)
#     qantity = models.IntegerField()
#     motif = models.CharField(max_length=255)
#     date_use_start = models.DateTimeField()
#     quantity_rewind = models.DateTimeField(null=True, blank=True)
    
#     @classmethod
#     def create_wording_cash_transaction(cls,user, cash_transactionst_id, 
#                              beneficiary_id, designation,qantity, 
#                              motif, date_use_start, quantity_rewind):
#         """
#         Crée une fiche de libellé de DMD.
        
#         Parameters:
#             employer_initiateur (str): Employeur initiateur.
#             ... # Inclure les autres paramètres
#         Returns:
#             CashTransaction or None: La fiche de dépenses créée ou None en cas d'erreur.
#         """
#         wording_cash_transaction = WordingCashTransaction()
#         wording_cash_transaction.cash_transactionst_id = cash_transactionst_id
#         wording_cash_transaction.beneficiary_id = beneficiary_id
#         wording_cash_transaction.designation = designation
#         wording_cash_transaction.qantity = qantity
#         wording_cash_transaction.motif = motif
#         wording_cash_transaction.date_use_start = date_use_start
#         wording_cash_transaction.quantity_rewind = quantity_rewind
#         wording_cash_transaction.num_ref = generate_unique_num_ref(WordingCashTransaction)

#         try:
#             with transaction.atomic():
#                 wording_cash_transaction._change_reason = json.dumps({"reason": "CREATE",
#                                                            "user": user})
#                 wording_cash_transaction.save()
#             return wording_cash_transaction
#         except DatabaseError as e:
#             print(f"Error when creating the expense sheet : {e}")
#             return None
        
#     @classmethod
#     def update_wording_cash_transaction(cls, wording_cash_transaction_id, user, cash_transactionst_id, 
#                                             beneficiary_id, designation,qantity,num_ref, 
#                                             motif, date_use_start, quantity_rewind):
#         """
#         Met à jour le libellé d'une DMD avec les données fournies.
        
#         Parameters:
#             data (dict): Dictionnaire contenant les champs à mettre à jour.
#         """
#         wording_cash_transaction = WordingCashTransaction.objects.get(id=wording_cash_transaction_id)
#         wording_cash_transaction.cash_transactionst_id = cash_transactionst_id
#         wording_cash_transaction.beneficiary_id = beneficiary_id
#         wording_cash_transaction.designation = designation
#         wording_cash_transaction.qantity = qantity
#         wording_cash_transaction.motif = motif
#         wording_cash_transaction.date_use_start = date_use_start
#         wording_cash_transaction.quantity_rewind = quantity_rewind
#         wording_cash_transaction.num_ref = num_ref
#         try:
#             with transaction.atomic():
#                 wording_cash_transaction._change_reason = json.dumps({"reason": "UPDATED",
#                                                            "user": user})
#                 wording_cash_transaction.save()
#             return wording_cash_transaction
#         except DatabaseError as e:
#             print(f"Error while updating the expense sheet : {e}")
#             return None   

#     @classmethod
#     def delete_wording_cash_transaction(cls, user: str, wording_cash_transaction_id: str):
#         """ delete cash_transaction """
        
#         try:
#             with transaction.atomic():
#                 cash_transaction_instance = cls.objects.get(id = wording_cash_transaction_id)  # Remplacez ... par votre logique pour récupérer l'objet CashTransaction
#                 cash_transaction_instance.is_active = False
#                 cash_transaction_instance._change_reason = json.dumps({"reason": "DELETE", "user": user})
#                 cash_transaction_instance.save()

#             return cash_transaction_instance
#         except cls.DoesNotExist:
#             return None
#         except DatabaseError:
#             return None
        
        
#     @classmethod
#     def restore_wording_cash_transaction(cls, user: str, wording_cash_transaction_id: str):
#         """ Restore cash_transaction """
        
#         try:
#             with transaction.atomic():
#                 cash_transaction_instance = cls.objects.get(id = wording_cash_transaction_id)  # Remplacez ... par votre logique pour récupérer l'objet CashTransaction
#                 cash_transaction_instance.is_active = True
#                 cash_transaction_instance._change_reason = json.dumps({"reason": "RESTORE", "user": user})
#                 cash_transaction_instance.save()
                
#             return cash_transaction_instance
#         except cls.DoesNotExist:
#             return None
#         except DatabaseError:
#             return None
        
        
#     def __str__(self):
#         return self.num_ref

    

# class Denomination(BaseUUIDModel):
#     employer_initiateur = models.CharField(max_length=255)
#     num_ref = models.CharField(max_length=255, unique=True)
#     value = models.FloatField()
#     count = models.IntegerField()
#     time_created = models.DateTimeField(auto_now_add=True)
#     time_updated = models.DateTimeField(auto_now=True)

#     def increment_count(self):
#         self.count += 1

#     def decrement_count(self):
#         self.count -= 1

#     def get_value(self):
#         return self.value * self.count

# class Currency(BaseUUIDModel):
#     employer_initiateur = models.CharField(max_length=255)
#     num_ref = models.CharField(max_length=255, unique=True)
#     name = models.CharField(max_length=200)
#     denominations = models.ManyToManyField(Denomination)
#     time_created = models.DateTimeField(auto_now_add=True)
#     time_updated = models.DateTimeField(auto_now=True)

#     def add_denomination(self, denomination):
#         self.denominations.add(denomination)

#     def remove_denomination(self, denomination):
#         self.denominations.remove(denomination)

#     def get_total_value(self):
#         return sum([denomination.get_value() for denomination in self.denominations.all()])

# class CashRegister(BaseUUIDModel):
#     employer_initiateur = models.CharField(max_length=255)
#     num_ref = models.CharField(max_length=255, unique=True)
#     currencies = models.ManyToManyField(Currency)
#     time_created = models.DateTimeField(auto_now_add=True)
#     time_updated = models.DateTimeField(auto_now=True)
#     type_cash_register_action = models.CharField(
#         max_length=255,
#         choices=[(choice.value, choice.name) for choice in TypeCashRegisterAction],
#         default=TypeCashRegisterAction.OPENING.value
#     )
#     site = models.CharField(max_length=255)
#     entite = models.CharField(max_length=255)

#     def add_currency(self, currency):
#         self.currencies.add(currency)

#     def remove_currency(self, currency):
#         self.currencies.remove(currency)

#     def get_total_value(self):
#         return sum([currency.get_total_value() for currency in self.currencies.all()])




# # Create Attachement Availability Reque here.
# class Currency(BaseUUIDModel):
#     num_ref = models.CharField(max_length=255, unique=True)
#     name = models.CharField(max_length=255)
#     cash_transactionst_id = models.ForeignKey(CashTransaction, on_delete=models.SET_NULL, null=True)
    
#     @classmethod
#     def create_attachement_cash_transaction(cls,user, cash_transactionst_id, 
#                              filename):
#         """
#         Crée une pièce-jointes de DMD.
        
#         Parameters:
#             employer_initiateur (str): Employeur initiateur.
#             ... # Inclure les autres paramètres
#         Returns:
#             CashTransaction or None: La fiche de dépenses créée ou None en cas d'erreur.
#         """
#         attachement_cash_transaction = AttachementCashTransaction()
#         attachement_cash_transaction.cash_transactionst_id = cash_transactionst_id
#         attachement_cash_transaction.filename = filename
#         attachement_cash_transaction.num_ref = generate_unique_num_ref(WordingCashTransaction)

#         try:
#             with transaction.atomic():
#                 attachement_cash_transaction._change_reason = json.dumps({"reason": "CREATE",
#                                                            "user": user})
#                 attachement_cash_transaction.save()
#             return attachement_cash_transaction
#         except DatabaseError as e:
#             print(f"Error when creating the expense sheet : {e}")
#             return None
        
#     @classmethod
#     def update_attachement_cash_transaction(cls, attachement_cash_transaction_id, user, 
#                                             cash_transactionst_id, filename, num_ref):
#         """
#         Met à jour une pièce-jointes avec les données fournies.
        
#         Parameters:
#             data (dict): Dictionnaire contenant les champs à mettre à jour.
#         """
#         wording_cash_transaction = WordingCashTransaction.objects.get(id=attachement_cash_transaction_id)
#         wording_cash_transaction.cash_transactionst_id = cash_transactionst_id
#         wording_cash_transaction.filename = filename
#         wording_cash_transaction.num_ref = num_ref
#         try:
#             with transaction.atomic():
#                 wording_cash_transaction._change_reason = json.dumps({"reason": "UPDATED",
#                                                            "user": user})
#                 wording_cash_transaction.save()
#             return wording_cash_transaction
#         except DatabaseError as e:
#             print(f"Error while updating the expense sheet : {e}")
#             return None 
    
    
#     def __str__(self):
#         return self.num_ref
