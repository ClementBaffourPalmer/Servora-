from rest_framework.permissions import BasePermission


class IsAuthenticatedProvider(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "is_provider", False))


class IsAuthenticatedCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "is_customer", False))

