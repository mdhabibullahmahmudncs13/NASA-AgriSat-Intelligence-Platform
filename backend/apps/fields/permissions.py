from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'farm'):
            return obj.farm.owner == request.user
        elif hasattr(obj, 'field'):
            return obj.field.farm.owner == request.user
        
        return False

class IsFarmOwner(permissions.BasePermission):
    """
    Custom permission to only allow farm owners to access farm-related data.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'farm'):
            return obj.farm.owner == request.user
        elif hasattr(obj, 'field'):
            return obj.field.farm.owner == request.user
        
        return False

class IsFieldOwner(permissions.BasePermission):
    """
    Custom permission to only allow field owners to access field-related data.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'farm'):
            return obj.farm.owner == request.user
        elif hasattr(obj, 'field'):
            return obj.field.farm.owner == request.user
        
        return False