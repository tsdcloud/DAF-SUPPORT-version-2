# depenses/serializers.py
from rest_framework import serializers
from .models import ReturnToCashier
from common.constances import PaymentMethods

class ReturnToCashierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnToCashier
        fields = '__all__'
        

class ReturnToCashierBaseSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    payment_method = serializers.ChoiceField(choices=[(payment.value, payment.name) for payment in PaymentMethods])
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    class Meta:
        model = ReturnToCashier
        fields = [
            'employer_initiateur',
            'expense_sheet_id',
            'description',
            'remaining_balance',
            'payment_method',
            'num_dossier',
            'site',
            'entite',
        ]
        
        
class ReturnToCashierCreateSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    payment_method = serializers.ChoiceField(choices=[(payment.value, payment.name) for payment in PaymentMethods])
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    class Meta:
        model = ReturnToCashier
        fields = [
            'expense_sheet_id',
            'description',
            'remaining_balance',
            'payment_method',
            'num_dossier',
            'site',
            'entite',
        ]
        
        
        
class ReturnToCashierListingSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    payment_method = serializers.ChoiceField(choices=[(payment.value, payment.name) for payment in PaymentMethods])
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    class Meta:
        model = ReturnToCashier
        fields = [
            'id',
            'num_ref',
            'statut',
            'employer_initiateur',
            'expense_sheet_id',
            'description',
            'remaining_balance',
            'payment_method',
            'num_dossier',
            'site',
            'entite',
            'is_active',
        ]
        
        
class ReturnToCashierDetailSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    payment_method = serializers.ChoiceField(choices=[(payment.value, payment.name) for payment in PaymentMethods])
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    class Meta:
        model = ReturnToCashier
        fields = [
            'id',
            'num_ref',
            'statut',
            'employer_initiateur',
            'expense_sheet_id',
            'description',
            'remaining_balance',
            'payment_method',
            'num_dossier',
            'site',
            'entite',
            'date_init',
            'is_active',
        ]
        

class ReturnToCashierValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnToCashier
        fields = [
            'description',
        ]
        
           

class ReturnToCashierValidationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        code = serializers.CharField(max_length=4)
           