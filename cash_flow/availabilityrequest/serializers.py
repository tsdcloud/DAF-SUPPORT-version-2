from rest_framework import serializers
from .models import AvailabilityRequest

class AvailabilityRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityRequest
        fields = '__all__'
        

class AvailabilityRequestBaseSerializer(serializers.ModelSerializer):
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
        # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
        num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
        
class AvailabilityRequestCreateSerializer(serializers.ModelSerializer):
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
        # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
        num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
        
        
class AvailabilityRequestListingSerializer(serializers.ModelSerializer):
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
            'site',
            'entite',
            'is_active',
        ]
        # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
        num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
        
class AvailabilityRequestDetailSerializer(serializers.ModelSerializer):
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
            'site',
            'entite',
            'date_init',
            'is_active',
        ]
        # Vous pouvez rendre des champs spécifiques optionnels en ajustant les paramètres suivants :
        num_dossier = serializers.CharField(max_length=50, required=False, allow_blank=True)
        observation_controleur = serializers.CharField(required=False, allow_blank=True)
        observation_ordonnateur = serializers.CharField(required=False, allow_blank=True)
        employer_compta_mat = serializers.CharField(max_length=255, required=False, allow_blank=True)
        date_valid_controleur = serializers.DateTimeField(null=True, blank=True)
        date_valid_ordonnateur = serializers.DateTimeField(null=True, blank=True)
        date_valid_compta_mat = serializers.DateTimeField(null=True, blank=True)

class AvailabilityRequestValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityRequest
        fields = [
            'description',
        ]
        
           

class AvailabilityRequestValidationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        code = serializers.CharField(max_length=4)
           