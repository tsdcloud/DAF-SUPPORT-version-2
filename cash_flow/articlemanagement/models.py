from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from common.models import BaseUUIDModel
import http.client
import json
from common.middleware import generate_unique_num_ref
from common.constances import ENDPOINT_ENTITY, ENDPOINT_USER
from django.core.mail import send_mail, send_mass_mail
from datetime import datetime

from django.db import DatabaseError, transaction
from common.constances import H_OPERATION_CHOICE,StatutAvailabilityReque, TYpeProduit, Module

from rest_framework.response import Response
from rest_framework import status

# def generate_unique_num_ref():
#     # NUM_REF peut être défini dynamiquement ou statiquement en fonction de vos besoins
#     NUM_REF = 10001
#     # Obtenez le mois/année actuel au format MM/YYYY
#     codefin = datetime.now().strftime("%m/%Y")
#     # Comptez le nombre d'objets avec une num_ref se terminant par le codefin actuel
#     count = AvailabilityReque.objects.filter(num_ref__endswith=codefin).count()
#     # Calculez le nouvel ID en ajoutant le nombre d'objets actuels à NUM_REF
#     new_id = NUM_REF + count
#     # Concaténez le nouvel ID avec le codefin pour former la nouvelle num_ref
#     concatenated_num_ref = f"{new_id}/{codefin}"
#     # concatenated_num_ref = str(new_id) + "/" + str(codefin) #f"{new_id}/{codefin}"
#     return concatenated_num_ref


# Create your Family Article here.
class FamilyArticle(BaseUUIDModel):
    num_ref = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255)
    sigle = models.CharField(max_length=255)
    type_module = models.CharField(
        max_length=255,
        choices=[(choice.value, choice.value) for choice in Module],  # Modifier pour utiliser choice.value
        default=Module.DMD.value
    )
    site = models.CharField(max_length=255)
    entite = models.CharField(max_length=255)
    create_by = models.CharField(max_length=255)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    @classmethod
    def create_family_article(cls, user, 
                             label, sigle, type_module, 
                             site, entite):
        """
        Crée une famille d'article.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            ExpenseSheet or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        family_article = FamilyArticle()

        family_article.label = label
        family_article.sigle = sigle.upper()
        family_article.type_module = type_module.upper()
        family_article.site = site
        family_article.entite = entite
        family_article.num_ref = generate_unique_num_ref(FamilyArticle)

        try:
            with transaction.atomic():
                family_article._change_reason = json.dumps({"reason": "CREATE",
                                                           "user": user})
                family_article.save()
            return family_article
        except DatabaseError as e:
            print(f"Error when creating the expense sheet : {e}")
            return None
    
    def update_family_article(cls,family_article_id,  user, 
                             label, sigle, type_module, 
                             site, entite):
        """
        Met à jour une fiche damille d'article avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        family_article = FamilyArticle.objects.get(id=family_article_id)
        
        family_article.label = label
        family_article.sigle = sigle.upper()
        family_article.type_module = type_module.upper()
        family_article.site = site
        family_article.entite = entite
        family_article.num_ref = generate_unique_num_ref()
        try:
            with transaction.atomic():
                family_article._change_reason = json.dumps({"reason": "UPDATED",
                                                           "user": user})
                family_article.save()
            return family_article
        except DatabaseError as e:
            print(f"Error while updating the article family : {e}")
            return None  

    @classmethod
    def delete_family_article(cls, user: str, family_article_id: str):
        """ delete family articles """
        
        try:
            with transaction.atomic():
                family_article_instance = cls.objects.get(id = family_article_id)  # Remplacez ... par votre logique pour récupérer l'objet ExpenseSheet
                family_article_instance.is_active = False
                family_article_instance._change_reason = json.dumps({"reason": "DELETE", "user": user})
                family_article_instance.save()

            return family_article_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
    
    @classmethod
    def restore_family_article(cls, user: str, family_article_id: str):
        """ Restore expense_sheet """
        
        try:
            with transaction.atomic():
                family_article_instance = cls.objects.get(id = family_article_id)  # Remplacez ... par votre logique pour récupérer l'objet ExpenseSheet
                family_article_instance.is_active = True
                family_article_instance._change_reason = json.dumps({"reason": "RESTORE", "user": user})
                family_article_instance.save()
                
            return family_article_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
        
    def __str__(self):
        return self.num_ref

# Create your Article here.
class Article(BaseUUIDModel):
    
    num_ref = models.CharField(max_length=255, unique=True)
    family_article_id = models.ForeignKey(FamilyArticle, on_delete=models.PROTECT)  # Modifier le champ pour utiliser on_delete=models.PROTECT
    label = models.CharField(max_length=255)
    sigle = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    
    create_by = models.CharField(max_length=255)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    
    @classmethod
    def create_article(cls, user,family_article_id, 
                             label, sigle, description):
        """
        Crée une famille d'article.
        
        Parameters:
            employer_initiateur (str): Employeur initiateur.
            ... # Inclure les autres paramètres
        Returns:
            ExpenseSheet or None: La fiche de dépenses créée ou None en cas d'erreur.
        """
        article = Article()

        article.label = label
        article.family_article_id = family_article_id
        article.sigle = sigle.upper()
        article.description = description.upper()
        article.num_ref = generate_unique_num_ref(Article)

        try:
            with transaction.atomic():
                article._change_reason = json.dumps({"reason": "CREATE",
                                                           "user": user})
                article.save()
            return article
        except DatabaseError as e:
            print(f"Error when creating the article : {e}")
            return None
    
    def update_article(cls, user,article_id, 
                             label, sigle, description, 
                             family_article_id):
        """
        Met à jour une fiche damille d'article avec les données fournies.
        
        Parameters:
            data (dict): Dictionnaire contenant les champs à mettre à jour.
        """
        article = FamilyArticle.objects.get(id=article_id)
        
        article.label = label
        article.sigle = sigle.upper()
        article.family_article_id = family_article_id
        article.sigle = sigle.upper()
        article.description = description.upper()
        article.num_ref = generate_unique_num_ref()
        try:
            with transaction.atomic():
                article._change_reason = json.dumps({"reason": "UPDATED",
                                                           "user": user})
                article.save()
            return article
        except DatabaseError as e:
            print(f"Error while updating the article : {e}")
            return None  

    @classmethod
    def delete_article(cls, user: str, article_id: str):
        """ delete family articles """
        
        try:
            with transaction.atomic():
                article_instance = cls.objects.get(id = article_id)  # Remplacez ... par votre logique pour récupérer l'objet ExpenseSheet
                article_instance.is_active = False
                article_instance._change_reason = json.dumps({"reason": "DELETE", "user": user})
                article_instance.save()

            return article_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None
    
    @classmethod
    def restore_article(cls, user: str, article_id: str):
        """ Restore expense_sheet """
        
        try:
            with transaction.atomic():
                article_instance = cls.objects.get(id = article_id)  # Remplacez ... par votre logique pour récupérer l'objet ExpenseSheet
                article_instance.is_active = True
                article_instance._change_reason = json.dumps({"reason": "RESTORE", "user": user})
                article_instance.save()
                
            return article_instance
        except cls.DoesNotExist:
            return None
        except DatabaseError:
            return None  

    def __str__(self):
        return self.num_ref
    

