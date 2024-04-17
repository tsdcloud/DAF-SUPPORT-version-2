from rest_framework.permissions import BasePermission


class IsAddCashTransaction(BasePermission):
    """ add cash_transaction """

    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'add_cash_transaction' in user['member']['user_permissions']:
                return True
            else:
                return False


class IsViewAllCashTransaction(BasePermission):
    """ view all cash_transaction """
    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'view_cash_transaction_all' in user['member']['user_permissions']:
                return True
            else:
                return False


class IsViewDetailCashTransaction(BasePermission):
    """ view detail cash_transaction """
    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'view_cash_transaction_detail' in user['member']['user_permissions']:
                return True
            else:
                return False


class IsChangeCashTransaction(BasePermission):
    """ update cash_transaction """
    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'change_cash_transaction' in user['member']['user_permissions']:
                return True
            else:
                return False


class IsDestroyCashTransaction(BasePermission):
    """ destroy cash_transaction """
    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'delete_cash_transaction' in user['member']['user_permissions']:
                return True
            else:
                return False


class IsValidateCashTransaction(BasePermission):
    """ validate cash_transaction """
    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'validate_cash_transaction' in user['user']['user_permissions']:
                return True
            else:
                return False

class IsRejecteCashTransaction(BasePermission):
    """ validate cash_transaction """
    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'reject_cash_transaction' in user['user']['user_permissions']:
                return True
            else:
                return False

class IsRestoreCashTransaction(BasePermission):
    """ restore cash_transaction """
    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'restore_cash_transaction' in user['user']['user_permissions']:
                return True
            else:
                return False

class IsGenerateCodeCashTransaction(BasePermission):
    """ restore cash_transaction """
    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'generate_code_cash_transaction' in user['user']['user_permissions']:
                return True
            else:
                return False

class IsValidateCodeCashTransaction(BasePermission):
    """ restore cash_transaction """
    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'validate_code_cash_transaction' in user['user']['user_permissions']:
                return True
            else:
                return False
            
