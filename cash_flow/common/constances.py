from django.conf import settings
from django.utils.translation import gettext_lazy as _
from enum import Enum

ENDPOINT_USER = "bfc.api.user.zukulufeg.com"

ENDPOINT_ENTITY = "bfc.api.entity.zukulufeg.com"

if not getattr(settings, "DEBUG"):
    ENDPOINT_USER = "bfc.api.user.zukulufeg.com"
    ENDPOINT_ENTITY = "bfc.api.entity.zukulufeg.com"
else:
    ENDPOINT_USER = getattr(settings, 'ENDPOINT_USER', None)
    ENDPOINT_ENTITY = getattr(settings, 'ENDPOINT_ENTITY', None)


class H_OPERATION_CHOICE(Enum):
    CREATE = 'CREATE'
    LIST = 'LIST'
    RITRIEVE = 'RITRIEVE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    VALIDATION = 'VALIDATION'
    REJECTION = 'REJECTION'
    RESTORE = 'RESTORE'
    

class StatutExpenseSheet(Enum):
    VALIDATION_CONFORMITE = 'VALIDATION CONFORMITE'
    REJET_CONFORMITE = 'REJET CONFORMITE'
    VALIDATION_BUDGETAIRE = 'VALIDATION BUDGETAIRE'
    REJET_BUDGETAIRE = 'REJET BUDGETAIRE'
    VALIDATION_ORDONNATEUR = 'VALIDATION ORDONNATEUR'
    REJET_ORDONNATEUR = 'REJET ORDONNATEUR'
    VALIDATION_DECAISSEMENT = 'VALIDATION DECAISSEMENT'
    REJET = 'REJET'
    EN_EXECUTION ='EN EXECUTION'
    ARCHIVE ='EXECUTE'

class PaymentMethods(Enum):
    ESPECES = 'ESPECES'
    CARTE = 'CARTE'
    VIREMENT = 'VIREMENT'
    CHEQUE = 'CHEQUE'
    PAIMENT_MOBILE = 'PAIMENT MOBILE'
    CRYPTO_MONAIE = 'REJET ORDONNATEUR'
    PORTE_MONAIE_ELECTRONIQUE = 'PORTE MONAIE ELECTRONIQUE'


# DMD constances
class StatutAvailabilityRequest(Enum):
    VALIDATION_CONTROLEUR = 'VALIDATION CONTROLEUR'
    REJET_CONTROLEUR = 'REJET CONTROLEUR'
    VALIDATION_ORDONNATEUR = 'VALIDATION ORDONNATEUR'
    REJET_ORDONNATEUR = 'REJET ORDONNATEUR'
    VALIDATION_COMPTABLE_MATIERE = 'VALIDATION COMPTABLE MATIERE'
    RECU = 'RECU'

class StatutReturnToCashier(Enum):
    VALIDATION_CAISSE = 'VALIDATION CAISSE'
    RECU = 'RECU'

class TypeProduit(Enum):
    BIEN = 'BIEN'
    SERVICE = 'SERVICE'

class Priorities(Enum):
    WEAK = 1
    MEDIUM = 2
    HIGH = 3

# gestion des modules    
class Module(Enum):
    DMD = 'DMD'
    BON_SORTIE_MATERIEL = 'BON SORTIE MATERIEL'
    DEPENSE = 'DEPENSE'
    RECETTE = 'RECETTE'
    RETOUR_CAISSE = 'RETOUR CAISSE'
    APPROVISIONNEMENT_CAISSE = 'APPROVISIONNEMENT CAISSE'

class TransactionType(Enum):
    CHECKIN = 'CHECKIN'
    CHECKOUT = 'CHECKOUT'

class TypeCashRegisterAction(Enum):
    OPENING = 'OPENING'
    CLOSING = 'CLOSING'
    
    
class TransactionStatus(Enum):
    NOT_EXECUTED = 'NOT EXECUTED'
    EXECUTED = 'EXECUTED'
    

    

    

BUSINESS_TYPE = [
    ("PRIVATE", _("PRIVATE")),
    ("CORPORATE", _("CORPORATE"))
]

ACCEPT_IMAGE = ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG"]

MAX_IMAGE_SIZE = 1000000