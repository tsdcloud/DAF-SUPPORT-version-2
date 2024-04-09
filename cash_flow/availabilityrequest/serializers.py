from rest_framework import serializers
from .models import AvailabilityRequest, WordingAvailabilityRequest
from common.constances import TypeProduit, Priorities
class AvailabilityRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityRequest
        fields = '__all__'
        

class AvailabilityRequestBaseSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    type_produit = serializers.ChoiceField(choices=[(type.value, type.name) for type in TypeProduit])
    class Meta:
        model = AvailabilityRequest
        fields = [
            'employer_controleur',
            'employer_ordonnateur',
            'requesting_service',
            'description',
            'type_produit',
            'num_dossier',
            'site',
            'entite',
        ]
        
        
class AvailabilityRequestCreateSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    type_produit = serializers.ChoiceField(choices=[(type.value, type.name) for type in TypeProduit])
    class Meta:
        model = AvailabilityRequest
        fields = [
            'employer_controleur',
            'employer_ordonnateur',
            'requesting_service',
            'description',
            'type_produit',
            'num_dossier',
            'site',
            'entite',
        ]
        
        
        
class AvailabilityRequestListingSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    type_produit = serializers.ChoiceField(choices=[(type.value, type.name) for type in TypeProduit])
    priority = serializers.ChoiceField(choices=[(level.value, level.name) for level in Priorities], required=False, allow_null=True, default=Priorities.WEAK.value)
    class Meta:
        model = AvailabilityRequest
        fields = [
            'id',
            'num_ref',
            'statut',
            'employer_initiateur',
            'employer_controleur',
            'employer_ordonnateur',
            'requesting_service',
            'description',
            'num_dossier',
            'type_produit',
            'priority',
            'site',
            'entite',
            'is_active',
        ]
        
        
class AvailabilityRequestDetailSerializer(serializers.ModelSerializer):
    # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
    num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
    observation_controleur = serializers.CharField(required=False, allow_blank=True)
    observation_ordonnateur = serializers.CharField(required=False, allow_blank=True)
    employer_compta_mat = serializers.CharField(max_length=255, required=False, allow_blank=True)
    type_produit = serializers.ChoiceField(choices=[(type.value, type.name) for type in TypeProduit])
    priority = serializers.ChoiceField(choices=[(level.value, level.name) for level in Priorities], required=False, allow_null=True, default=Priorities.WEAK.value)
    date_valid_controleur = serializers.DateTimeField(allow_null=True, required=False)
    date_valid_ordonnateur = serializers.DateTimeField(allow_null=True, required=False)
    date_valid_compta_mat = serializers.DateTimeField(allow_null=True, required=False)
    class Meta:
        model = AvailabilityRequest
        fields = [
            'id',
            'num_ref',
            'statut',
            'employer_initiateur',
            'employer_controleur',
            'employer_ordonnateur',
            'requesting_service',
            'description',
            'type_produit',
            'site',
            'entite',
            'num_dossier',
            
            'observation_controleur',
            'observation_ordonnateur',
            'date_valid_controleur',
            'date_valid_ordonnateur',
            'date_valid_compta_mat',
            
            'date_valid_controleur',
            'date_valid_ordonnateur',
            'date_valid_compta_mat',
            'employer_compta_mat',
            'priority',
            'site',
            'entite',
            'time_created',
            'is_active',
        ]
        

class AvailabilityRequestValidationSerializer(serializers.ModelSerializer):
    priority = serializers.ChoiceField(choices=[(level.value, level.name) for level in Priorities], required=False, allow_null=True, default=Priorities.WEAK.value)
    class Meta:
        model = AvailabilityRequest
        fields = [
            'description',
            'priority',
        ]
        
           

class AvailabilityRequestValidationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        code = serializers.CharField(max_length=4)



# Wording Availability Request SERIALIZERS
class WordingAvailabilityRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordingAvailabilityRequest
        fields = '__all__'

class WordingAvailabilityRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordingAvailabilityRequest
        fields = [
            'label',
            'sigle',
            'family_article_id',
            'description',
        ]

class WordingAvailabilityRequestListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordingAvailabilityRequest
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