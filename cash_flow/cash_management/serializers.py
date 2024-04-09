from rest_framework import serializers
from .models import CashTransaction, WordingCashTransaction

class CashTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransaction
        fields = '__all__'
        

class CashTransactionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransaction
        fields = [
            'cashier_id',
            'employer_initiateur',
            'montant',
            'transaction_type',
            'module',
            'item_id',
            'num_dossier',
            'employer_beneficiaire',
            'code_validation',
            'date_valid_beneficiaire',
            'site',
            'entite',
        ]
        # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
        num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
        employer_beneficiaire = serializers.CharField(max_length=255, required=False, allow_blank=True)
        code_validation = serializers.IntegerField(max_length=4, null=True, blank=True)
        date_valid_beneficiaire = serializers.DateTimeField(allow_null=True, required=False)
        
        
class CashTransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransaction
        fields = [
            'cashier_id',
            'employer_initiateur',
            'montant',
            'transaction_type',
            'module',
            'item_id',
            'num_dossier',
            'employer_beneficiaire',
            'code_validation',
            'date_valid_beneficiaire',
            'site',
            'entite',
        ]
        # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
        num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
        employer_beneficiaire = serializers.CharField(max_length=255, required=False, allow_blank=True)
        code_validation = serializers.IntegerField(max_length=4, null=True, blank=True)
        date_valid_beneficiaire = serializers.DateTimeField(allow_null=True, required=False)
        
        
class CashTransactionListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransaction
        fields = [
            'id',
            'num_ref',
            'statut',
            'cashier_id',
            'employer_initiateur',
            'montant',
            'transaction_type',
            'module',
            'item_id',
            'num_dossier',
            'employer_beneficiaire',
            'code_validation',
            'date_valid_beneficiaire',
            'site',
            'entite',
            'is_active',
        ]
        # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
        num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
        employer_beneficiaire = serializers.CharField(max_length=255, required=False, allow_blank=True)
        code_validation = serializers.IntegerField(max_length=4, null=True, blank=True)
        date_valid_beneficiaire = serializers.DateTimeField(allow_null=True, required=False)
        
class CashTransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransaction
        fields = [
            'id',
            'num_ref',
            'statut',
            'cashier_id',
            'employer_initiateur',
            'montant',
            'transaction_type',
            'module',
            'item_id',
            'num_dossier',
            'employer_beneficiaire',
            'code_validation',
            'date_valid_beneficiaire',
            'site',
            'entite',
            'time_created',
            'is_active',
        ]
        # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
        num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
        employer_beneficiaire = serializers.CharField(max_length=255, required=False, allow_blank=True)
        code_validation = serializers.IntegerField(max_length=4, null=True, blank=True)
        date_valid_beneficiaire = serializers.DateTimeField(allow_null=True, required=False)

class CashTransactionValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransaction
        fields = [
            'code_validation',
        ]
        
           

class CashTransactionValidationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        code = serializers.CharField(max_length=4)



# Wording Availability Request SERIALIZERS
class WordingCashTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordingCashTransaction
        fields = '__all__'

class WordingCashTransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordingCashTransaction
        fields = [
            'label',
            'sigle',
            'family_article_id',
            'description',
        ]

class WordingCashTransactionListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordingCashTransaction
        fields = [
            'id',
            'num_ref',
            'family_article_id',
            'label',
            'sigle',
            'description',
            'time_created',
            'create_by',
            'is_active',
        ]