from rest_framework import serializers
from cash_management.models import CashTransaction
# WordingCashTransaction,
#                      CashRegister, Currency, Denomination)

class CashTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransaction
        fields = '__all__'
        

class CashTransactionBaseSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    employer_beneficiaire = serializers.CharField(max_length=255, required=False, allow_blank=True)
    date_valid_beneficiaire = serializers.DateTimeField(allow_null=True, required=False)
    
    class Meta:
        model = CashTransaction
        fields = [
            'employer_initiateur',
            'cashier_id',
            'montant',
            'transaction_type',
            'module',
            'item_id',
            'num_dossier',
            'employer_beneficiaire',
            'date_valid_beneficiaire',
            'site',
            'entite',
        ]
        
        
        
class CashTransactionCreateSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    employer_beneficiaire = serializers.CharField(max_length=255, required=False, allow_blank=True)
    # date_valid_beneficiaire = serializers.DateTimeField(allow_null=True, required=False)
    
    class Meta:
        model = CashTransaction
        fields = [
            'employer_beneficiaire',
            'cashier_id',
            'montant',
            'transaction_type',
            'module',
            'item_id',
            'num_dossier',
            'description',
            'site',
            'entite',
        ]
    
        
        
class CashTransactionListingSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    employer_beneficiaire = serializers.CharField(max_length=255, required=False, allow_blank=True)
    date_valid_beneficiaire = serializers.DateTimeField(allow_null=True, required=False)
    class Meta:
        model = CashTransaction
        fields = [
            'id',
            'num_ref',
            'status',
            'employer_initiateur',
            'employer_beneficiaire',
            'date_valid_beneficiaire',
            'cashier_id',
            'montant',
            'transaction_type',
            'module',
            'item_id',
            'num_dossier',
            'description',
            'site',
            'entite',
            'is_active',
        ]
        
        
class CashTransactionDetailSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    employer_beneficiaire = serializers.CharField(max_length=255, required=False, allow_blank=True)
    date_valid_beneficiaire = serializers.DateTimeField(allow_null=True, required=False)

    class Meta:
        model = CashTransaction
        fields = [
            'id',
            'num_ref',
            'status',
            'employer_initiateur',
            'employer_beneficiaire',
            'date_valid_beneficiaire',
            'cashier_id',
            'montant',
            'transaction_type',
            'module',
            'item_id',
            'num_dossier',
            'description',
            'site',
            'entite',
            'time_created',
            'is_active',
        ]
        

class CashTransactionValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransaction
        fields = [
            'code_validation',
        ]
    
    def validate_code_validation(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("Le code de validation doit être exactement 4 chiffres")
        return value
        
           

class CashTransactionValidationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashTransaction
        fields = [
            'code_validation',
        ]
    
    def validate_code_validation(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("Le code de validation doit être exactement 4 chiffres")
        return value
    
class CashTransactionGenerateCodeSerializer(serializers.ModelSerializer):
    date_valid_beneficiaire = serializers.DateTimeField(allow_null=True, required=False)
    class Meta:
        model = CashTransaction
        fields = [
            'date_valid_beneficiaire',
        ]



# Wording Availability Request SERIALIZERS
# Serializers define the API representation.
# class DenominationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Denomination
#         fields = ['value', 'count']

# class CurrencySerializer(serializers.ModelSerializer):
#     denominations = DenominationSerializer(many=True, read_only=True)

#     class Meta:
#         model = Currency
#         fields = ['name', 'denominations']

# class CashRegisterSerializer(serializers.ModelSerializer):
#     currencies = CurrencySerializer(many=True, read_only=True)

#     class Meta:
#         model = CashRegister
#         fields = ['currencies']