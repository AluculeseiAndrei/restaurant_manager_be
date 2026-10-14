from fastapi import Depends
from restaurant_api.core.config import Settings, get_settings
from restaurant_api.core.database import get_async_database
from restaurant_api.repositories.users import AsyncMongoUserRepository
from restaurant_api.repositories.restaurant import ClientRepository, FoodTypeRepository, MenuRepository, ProductRepository, ReservationRepository, TableRepository
from restaurant_api.repositories.employees import AsyncEmployeeRepository
from restaurant_api.services.auth import AuthenticationService
from restaurant_api.services.clients import ClientService
from restaurant_api.services.food_types import FoodTypeService
from restaurant_api.services.menus import MenuService
from restaurant_api.services.products import ProductService
from restaurant_api.services.reservations import ReservationService
from restaurant_api.services.tables import TableService
from restaurant_api.services.employees import EmployeeService
from restaurant_api.services.users import UserService
from restaurant_api.core.security import get_current_user_id
from fastapi import HTTPException


def get_user_repository(database=Depends(get_async_database)) -> AsyncMongoUserRepository:
    return AsyncMongoUserRepository(database["user"])


def get_authentication_service(
    repository: AsyncMongoUserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> AuthenticationService:
    return AuthenticationService(repository, settings)


def get_user_service(repository: AsyncMongoUserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository)


async def get_current_user(user_id: str = Depends(get_current_user_id), repository: AsyncMongoUserRepository = Depends(get_user_repository)) -> dict:
    user = await repository.find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Authenticated user not found")
    user["id"] = user_id
    if user.get("role") == "admin":
        user["restaurant_id"] = user_id
    elif user.get("role") != "client":
        employee = await repository.employee_for_user(user)
        user["restaurant_id"] = employee.get("userId") if employee else None
    return user


def require_owner(restaurant_id: str, user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin" or restaurant_id != user["id"]:
        raise HTTPException(status_code=403, detail="Restaurant owner access required")
    return user


def require_owner_for_admin(admin_id: str, user: dict = Depends(get_current_user)) -> dict:
    return require_owner(admin_id, user)


def require_owner_for_user_id(user_id: str, user: dict = Depends(get_current_user)) -> dict:
    return require_owner(user_id, user)


def require_staff_for_admin(admin_id: str, user: dict = Depends(get_current_user)) -> dict:
    return require_restaurant_staff(admin_id, user)


def require_staff_for_restaurant(restaurant_id: str, user: dict = Depends(get_current_user)) -> dict:
    return require_restaurant_staff(restaurant_id, user)


def require_staff_for_user_id(user_id: str, user: dict = Depends(get_current_user)) -> dict:
    return require_restaurant_staff(user_id, user)


def require_restaurant_staff(restaurant_id: str, user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") == "client" or user.get("restaurant_id") != restaurant_id:
        raise HTTPException(status_code=403, detail="You are not assigned to this restaurant")
    return user


def require_client(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "client":
        raise HTTPException(status_code=403, detail="Client access required")
    return user


def require_reservation_creator(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") not in {"client", "admin"}:
        raise HTTPException(status_code=403, detail="Client or restaurant owner access required")
    return user


async def get_client_service(database=Depends(get_async_database)) -> ClientService:
    return ClientService(ClientRepository(database))


async def get_table_service(database=Depends(get_async_database), settings: Settings = Depends(get_settings)) -> TableService:
    return TableService(TableRepository(database, settings.default_currency))


async def get_menu_service(database=Depends(get_async_database)) -> MenuService:
    return MenuService(MenuRepository(database))


async def get_product_service(database=Depends(get_async_database)) -> ProductService:
    return ProductService(ProductRepository(database))


async def get_reservation_service(database=Depends(get_async_database)) -> ReservationService:
    return ReservationService(ReservationRepository(database))


async def get_food_type_service(database=Depends(get_async_database)) -> FoodTypeService:
    return FoodTypeService(FoodTypeRepository(database))


async def get_employee_service(database=Depends(get_async_database)) -> EmployeeService:
    return EmployeeService(AsyncEmployeeRepository(database))


async def require_menu_owner(product_id: str, user: dict = Depends(get_current_user), database=Depends(get_async_database)) -> dict:
    from restaurant_api.repositories.restaurant import object_id
    product = await database["menu"].find_one({"_id": object_id(product_id, "product ID")})
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    return require_owner(product.get("adminId", ""), user)


async def require_table_staff(table_id: str, user: dict = Depends(get_current_user), database=Depends(get_async_database)) -> dict:
    from restaurant_api.repositories.restaurant import object_id
    table = await database["table"].find_one({"_id": object_id(table_id, "table ID")})
    if not table: raise HTTPException(status_code=404, detail="Table not found")
    return require_restaurant_staff(table.get("userId", ""), user)


async def require_product_staff(product_id: str, user: dict = Depends(get_current_user), database=Depends(get_async_database)) -> dict:
    from restaurant_api.repositories.restaurant import object_id
    product = await database["products"].find_one({"_id": object_id(product_id, "product ID")})
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    table = await database["table"].find_one({"_id": object_id(product.get("tableId", ""), "table ID")})
    if not table: raise HTTPException(status_code=404, detail="Table not found")
    return require_restaurant_staff(table.get("userId", ""), user)
