from rest_framework.permissions import BasePermission


class IsAddExpenseSheet(BasePermission):
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


class IsViewAllExpenseSheet(BasePermission):
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


class IsViewDetailExpenseSheet(BasePermission):
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


class IsChangeExpenseSheet(BasePermission):
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


class IsDestroyExpenseSheet(BasePermission):
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


class IsValidateExpenseSheet(BasePermission):
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

class IsRejecteExpenseSheet(BasePermission):
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

class IsRestoreExpenseSheet(BasePermission):
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
