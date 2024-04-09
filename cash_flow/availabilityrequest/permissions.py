from rest_framework.permissions import BasePermission


class IsAddAvailabilityRequest(BasePermission):
    """ add expense_sheet """

    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'add_expense_sheet' in user['member']['user_permissions']:
                return True
            else:
                # return True
                return False


class IsViewAllAvailabilityRequest(BasePermission):
    """ view all expense_sheet """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'view_expense_sheet_all' in user['member']['user_permissions']:
                return True
            else:
                # return True
                return False


class IsViewDetailAvailabilityRequest(BasePermission):
    """ view detail expense_sheet """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'view_expense_sheet_detail' in user['member']['user_permissions']:
                return True
            else:
                # return True
                return False


class IsChangeAvailabilityRequest(BasePermission):
    """ update expense_sheet """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'change_expense_sheet' in user['member']['user_permissions']:
                return True
            else:
                # return True
                return False


class IsDestroyAvailabilityRequest(BasePermission):
    """ destroy expense_sheet """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'delete_expense_sheet' in user['member']['user_permissions']:
                return True
            else:
                # return True
                return False


class IsValidateAvailabilityRequest(BasePermission):
    """ validate expense_sheet """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'validate_expense_sheet' in user['user']['user_permissions']:
                return True
            else:
                # return True
                return False

class IsRejecteAvailabilityRequest(BasePermission):
    """ validate expense_sheet """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'reject_expense_sheet' in user['user']['user_permissions']:
                return True
            else:
                # return True
                return False

class IsRestoreAvailabilityRequest(BasePermission):
    """ restore expense_sheet """
    def has_permission(self, request, view):
        if request.infoUser is None:
            # return True
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'restore_expense_sheet' in user['user']['user_permissions']:
                return True
            else:
                # return True
                return False


# Permission WordingAvailabilityRequest
class IsAddWordingAvailabilityRequest(BasePermission):
    """ add wordin availability request """

    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'add_wording_availability_request' in user['member']['user_permissions']:
                return True
            else:
                return False


class IsViewAllWordingAvailabilityRequest(BasePermission):
    """ view all wordin availability request """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'view__wording_availability_request_all' in user['member']['user_permissions']:
                return True
            else:
                
                return False


class IsChangeWordingAvailabilityRequest(BasePermission):
    """ update wordin availability request """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'change_wording_availability_request' in user['member']['user_permissions']:
                return True
            else:
                
                return False


class IsDestroyWordingAvailabilityRequest(BasePermission):
    """ destroy wording availability request """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'delete_wording_availability_request' in user['member']['user_permissions']:
                return True
            else:
                
                return False


class IsRestoreWordingAvailabilityRequest(BasePermission):
    """ restore wording availability request """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'restore_wording_availability_request' in user['user']['user_permissions']:
                return True
            else:
                
                return False