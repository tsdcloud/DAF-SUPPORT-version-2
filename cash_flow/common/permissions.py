from rest_framework.permissions import BasePermission


class IsDeactivate(BasePermission):

    def has_permission(self, request, view):
        return False

class IsActivate(BasePermission):

    def has_permission(self, request, view):
        return True
