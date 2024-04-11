# depenses/serializers.py
from rest_framework import serializers
from .models import ExpenseSheet
from common.constances import PaymentMethods

class ExpenseSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseSheet
        fields = '__all__'
        

class ExpenseSheetBaseSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    payment_method = serializers.ChoiceField(choices=[(payment.value, payment.name) for payment in PaymentMethods])
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    class Meta:
        model = ExpenseSheet
        fields = [
            'employer_initiateur',
            'employer_beneficiaire',
            'description',
            'montant',
            'payment_method',
            'num_dossier',
            'site',
            'entite',
        ]
        
        
class ExpenseSheetCreateSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    payment_method = serializers.ChoiceField(choices=[(payment.value, payment.name) for payment in PaymentMethods])
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    class Meta:
        model = ExpenseSheet
        fields = [
            # 'employer_initiateur',
            'employer_beneficiaire',
            'description',
            'montant',
            'payment_method',
            'num_dossier',
            'employer_conformite',
            'employer_budgetaire',
            'employer_ordonnateur',
            'site',
            'entite',
        ]
        
        
        
class ExpenseSheetListingSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    payment_method = serializers.ChoiceField(choices=[(payment.value, payment.name) for payment in PaymentMethods])
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    class Meta:
        model = ExpenseSheet
        fields = [
            'id',
            'num_ref',
            'statut',
            'employer_initiateur',
            'employer_beneficiaire',
            'description',
            'montant',
            'payment_method',
            'num_dossier',
            'date_init',
            'site',
            'entite',
            'is_active',
        ]
        
        
class ExpenseSheetDetailSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    payment_method = serializers.ChoiceField(choices=[(payment.value, payment.name) for payment in PaymentMethods])
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    observation_conformite = serializers.CharField(required=False, allow_blank=True)
    observation_budgetaire = serializers.CharField(required=False, allow_blank=True)
    observation_ordonnateur = serializers.CharField(required=False, allow_blank=True)
    employer_caissier = serializers.CharField(max_length=255, required=False, allow_blank=True)
    class Meta:
        model = ExpenseSheet
        fields = [
            'id',
            'num_ref',
            'statut',
            'employer_initiateur',
            'employer_beneficiaire',
            'description',
            'montant',
            'payment_method',
            'num_dossier',
            'employer_budgetaire',
            'employer_ordonnateur',
            'observation_conformite',
            'observation_budgetaire',
            'observation_ordonnateur',
            'employer_conformite',
            'employer_budgetaire',
            'employer_ordonnateur',
            'employer_caissier',
            'site',
            'entite',
            'date_init',
            'is_active',
        ]
        

class ExpenseSheetValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseSheet
        fields = [
            'description',
        ]
        
           

class ExpenseSheetValidationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        code = serializers.CharField(max_length=4)
           