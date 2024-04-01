import http.client
import json
from common.constances import ENDPOINT_USER, ENDPOINT_ENTITY
from django.core.mail import send_mail, send_mass_mail
from datetime import datetime
from cash_flow.settings import (
    DEFAULT_FROM_EMAIL,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_TIMEOUT,
    EMAIL_USE_TLS,
    DEFAULT_AUTHORIZATION
)


# Get infos USER by token
def auth_middleware(get_response):
    """Middleware pour récupérer l'utilisateur authentifié"""

    def middleware(request):
        # Étape 1 : Récupérer le jeton d'authentification depuis les en-têtes de la requête
        authorization = request.headers.get('Authorization', 'e')
        # print(authorization)
        # Étape 2 : Effectuer une requête HTTP pour récupérer les informations de l'utilisateur
        conn = http.client.HTTPSConnection(ENDPOINT_USER)
        payload = ''
        headers = {
            "Authorization": authorization
        }
        conn.request("GET", "/users/account/", payload, headers)
        response = conn.getresponse()
        data = json.loads(response.read())

        # Étape 3 : Vérifier si l'utilisateur est authentifié avec succès
        if data.get('id', 0) != 0:
            # Si oui, ajouter les informations de l'utilisateur à l'objet de requête
            request.infoUser = data
            
            # Étape 4 : Effectuer une autre requête pour obtenir les permissions de l'utilisateur
            conn1 = http.client.HTTPSConnection(ENDPOINT_ENTITY)
            conn1.request("GET", "/employee/permissions/", payload, headers)
            response1 = conn1.getresponse()
            data1 = json.loads(response1.read())
            
            # Étape 5 : Ajouter les permissions à l'objet de requête
            request.infoUser['member']['user_permissions'] = data1['permissions']
        else:
            # Si l'authentification échoue, définir infoUser à None
            request.infoUser = None

        # Étape 6 : Appeler la fonction suivante dans la chaîne de middleware
        response = get_response(request)

        # Étape 7 : Retourner la réponse finale
        return response

    return middleware

def generate_unique_num_ref(model):
    # NUM_REF peut être défini dynamiquement ou statiquement en fonction de vos besoins
    NUM_REF = 10001
    # Obtenez le mois/année actuel au format MM/YYYY
    codefin = datetime.now().strftime("%m/%Y")
    # Comptez le nombre d'objets avec une num_ref se terminant par le codefin actuel
    count = model.objects.filter(num_ref__endswith=codefin).count()
    # Calculez le nouvel ID en ajoutant le nombre d'objets actuels à NUM_REF
    new_id = NUM_REF + count
    # Concaténez le nouvel ID avec le codefin pour former la nouvelle num_ref
    concatenated_num_ref = f"{new_id}/{codefin}"
    # concatenated_num_ref = str(new_id) + "/" + str(codefin) #f"{new_id}/{codefin}"
    return concatenated_num_ref

# prendre l'email d'un utilisateur par son ID
def get_email_addressee(id_addressee: str):
    # conn = http.client.HTTPSConnection(ENDPOINT_USER)
    # payload = ''
    # headers = {
    # 'Authorization': f'Bearer {DEFAULT_AUTHORIZATION}'
    # }
    # conn.request(f"GET", "/users/{id_addressee}/", payload, headers)
    # res = conn.getresponse()
    
    print(id_addressee)
    
    conn = http.client.HTTPSConnection("bfc.api.user.zukulufeg.com")
    payload = ''
    headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA4MDgyMjc3LCJpYXQiOjE3MDc5OTU4NzcsImp0aSI6Ijk0ODRmYWEzZGYwYTRjMmRiMDhlMDk5YzQ1Njg5YzJjIiwidXNlcl9pZCI6ImFhNGJmMGUyLTEyNmEtNGI3Yy04ZDUwLWNlMDAzZDExZmIyMyJ9.L-aegcHKv1kcfCqsGWrn5j88eJZbK2bOuTkJe08MQ4M'
    }
    conn.request("GET", "/users/e2a1a56d-4c2d-4b2a-82eb-b51f6072f53d/", payload, headers)
    res = conn.getresponse()
    data = res.read()
    # print(data.decode("utf-8"))

    data = json.loads(res.read())

    print(data)
    
    e_mail = "data.email"
    return e_mail
    

    
# envois de mail
def send_email(
        subject: str,
        message: str,
        recipient_list,
        from_email = DEFAULT_FROM_EMAIL,
        fail_silently=False,
        auth_user=EMAIL_HOST_USER,
        auth_password=EMAIL_HOST_PASSWORD,
        connection=None,
        html_message=None
    ):
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently,
        auth_user,
        auth_password,
        connection,
        html_message,
    )
    return {"Message": "E-mail envoyé avec succès."}