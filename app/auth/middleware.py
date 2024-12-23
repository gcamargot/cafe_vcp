from fastapi import Depends, HTTPException, status
from typing import List, Callable
from .utils import oauth2_scheme, verify_token

def check_permissions(allowed_roles: List[str]) -> Callable:
    """
    Crea un middleware para verificar permisos basados en roles.

    Uso:
    @router.get("/ruta-protegida")
    async def ruta_protegida(
        _: None = Depends(check_permissions(["admin", "cashier"]))
    ):
        return {"message": "Acceso permitido"}
    """
    async def permission_checker(token: str = Depends(oauth2_scheme)):
        payload = await verify_token(token)
        user_role = payload.get("role")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso"
            )
        return payload

    return permission_checker
