from django.shortcuts import render
from .constances import ENDPOINT_USER, ENDPOINT_ENTITY

def my_view(request):
    # Utilisez ENDPOINT_USER et ENDPOINT_ENTITY comme nécessaire
    print(ENDPOINT_USER)
    print(ENDPOINT_ENTITY)

# Create your views here.
