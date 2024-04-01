from rest_framework.permissions import BasePermission


class IsAddFamilyArticle(BasePermission):
    """ add family article """

    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'add_family_article' in user['member']['user_permissions']:
                return True
            else:
                
                return False


class IsViewAllFamilyArticle(BasePermission):
    """ view all family article """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'view_family_article_all' in user['member']['user_permissions']:
                return True
            else:
                
                return False


class IsChangeFamilyArticle(BasePermission):
    """ update family article """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'change_family_article' in user['member']['user_permissions']:
                return True
            else:
                
                return False


class IsDestroyFamilyArticle(BasePermission):
    """ destroy family article """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'delete_family_article' in user['member']['user_permissions']:
                return True
            else:
                
                return False


class IsRestoreFamilyArticle(BasePermission):
    """ restore family article """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'restore_family_article' in user['user']['user_permissions']:
                return True
            else:
                
                return False

# Permission article
class IsAddArticle(BasePermission):
    """ add article """

    def has_permission(self, request, view):
        if request.infoUser is None:
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'add_article' in user['member']['user_permissions']:
                return True
            else:
                return False


class IsViewAllArticle(BasePermission):
    """ view all article """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'view_article_all' in user['member']['user_permissions']:
                return True
            else:
                
                return False


class IsChangeArticle(BasePermission):
    """ update article """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'change_article' in user['member']['user_permissions']:
                return True
            else:
                
                return False


class IsDestroyArticle(BasePermission):
    """ destroy article """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'delete_article' in user['member']['user_permissions']:
                return True
            else:
                
                return False


class IsRestoreArticle(BasePermission):
    """ restore article """
    def has_permission(self, request, view):
        if request.infoUser is None:
            
            return False
        else:
            user = request.infoUser
            if user['member'].get('is_superuser') is True:
                return True
            elif 'restore_article' in user['user']['user_permissions']:
                return True
            else:
                
                return False
