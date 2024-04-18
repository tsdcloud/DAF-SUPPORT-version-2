from rest_framework.permissions import BasePermission


class IsAddReturnToCashier(BasePermission):
    """ add return_to_cashier """

    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'add_return_to_cashier' in user['member']['user_permissions']:
                return True
            else:
                # return True
                return False


class IsViewAllReturnToCashier(BasePermission):
    """ view all return_to_cashier """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'view_return_to_cashier_all' in user['member']['user_permissions']:
                return True
            else:
                # return True
                return False


class IsViewDetailReturnToCashier(BasePermission):
    """ view detail return_to_cashier """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'view_return_to_cashier_detail' in user['member']['user_permissions']:
                return True
            else:
                # return True
                return False


class IsChangeReturnToCashier(BasePermission):
    """ update return_to_cashier """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'change_return_to_cashier' in user['member']['user_permissions']:
                return True
            else:
                # return True
                return False


class IsDestroyReturnToCashier(BasePermission):
    """ destroy return_to_cashier """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'delete_return_to_cashier' in user['member']['user_permissions']:
                return True
            else:
                # return True
                return False


class IsValidateReturnToCashier(BasePermission):
    """ validate return_to_cashier """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'validate_return_to_cashier' in user['user']['user_permissions']:
                return True
            else:
                # return True
                return False

class IsRejecteReturnToCashier(BasePermission):
    """ validate return_to_cashier """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'reject_return_to_cashier' in user['user']['user_permissions']:
                return True
            else:
                # return True
                return False

class IsRestoreReturnToCashier(BasePermission):
    """ restore return_to_cashier """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'restore_return_to_cashier' in user['user']['user_permissions']:
                return True
            else:
                # return True
                return False
