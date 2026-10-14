from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from bson import ObjectId

from restaurant_api.core.exceptions import DomainError
from restaurant_api.core.security import hash_password


def object_id(value: str, label: str = "ID") -> ObjectId:
    if not ObjectId.is_valid(value):
        raise DomainError(f"Invalid {label}", 400)
    return ObjectId(value)


def public_document(document: dict[str, Any] | None) -> dict[str, Any] | None:
    if document is None:
        return None
    result = dict(document)
    if "_id" in result:
        result["_id"] = str(result["_id"])
    for secret in ("password", "code", "resetCode"):
        result.pop(secret, None)
    return result


def money_to_cents(value: Any) -> int:
    return int((Decimal(str(value)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class ClientRepository:
    def __init__(self, database) -> None:
        self.users, self.reviews = database["user"], database["recensions"]

    async def create(self, data):
        if await self.users.find_one({"email": data["username"]}): raise DomainError("User with this email already exists", 409)
        result = await self.users.insert_one({"email": data["username"], "name": data["client_name"], "password": hash_password(data["password"]), "role": "client", "phoneNumber": data["phone_number"], "location": data["location"], "county": data["county"]})
        return str(result.inserted_id)

    async def restaurants(self, county=None, location=None, name=None):
        query = {"role": "admin"}
        if location: query["location"] = {"$regex": f"^{location}$", "$options": "i"}
        if county: query["county"] = {"$regex": f"^{county}$", "$options": "i"}
        if name: query["companyName"] = {"$regex": name, "$options": "i"}
        return [public_document(i) or {} for i in await self.users.find(query).to_list()]

    async def add_review(self, data):
        restaurant_id = object_id(data["restaurant_id"], "restaurant ID")
        restaurant = await self.users.find_one({"_id": restaurant_id, "role": "admin"})
        if not restaurant: raise DomainError("Restaurant not found", 404)
        await self.reviews.insert_one({"clientId": data["client_id"], "restaurantId": data["restaurant_id"], "recension": data["recension"], "rating": data["rating"], "createdAt": datetime.now(timezone.utc)})
        ratings = restaurant.get("totalRatings", []) + [data["rating"]]
        await self.users.update_one({"_id": restaurant_id}, {"$set": {"totalRatings": ratings, "totalRecensions": len(ratings), "finalRating": sum(ratings) / len(ratings)}})
        return {"message": "Review posted successfully"}

    async def reviews_for(self, restaurant_id):
        return [public_document(i) or {} for i in await self.reviews.find({"restaurantId": restaurant_id}).to_list()]

    async def update_location(self, data):
        result = await self.users.update_one({"_id": object_id(data["client_id"], "client ID"), "role": "client"}, {"$set": {"location": data["location"], "county": data["county"]}})
        if not result.matched_count: raise DomainError("Client not found", 404)
        return {"message": "Location updated successfully"}


class TableRepository:
    def __init__(self, database, currency: str = "RON") -> None:
        self.tables, self.products, self.users, self.history = database["table"], database["products"], database["user"], database["productHistory"]
        self.currency = currency

    async def create(self, data, user_id):
        user = await self.users.find_one({"_id": object_id(user_id, "user ID")})
        if not user: raise DomainError("The user does not exist", 404)
        owner_id = user_id if user.get("role") == "admin" else user.get("adminId")
        result = await self.tables.insert_one({"name": data["name"], "capacity": data.get("capacity"), "billValue": 0, "userId": owner_id})
        return str(result.inserted_id)

    async def list(self, user_id, page):
        if page < 1: raise DomainError("Page must be positive", 400)
        tables = await self.tables.find({"userId": user_id}).sort("name", 1).skip((page - 1) * 9).limit(9).to_list()
        if not tables: raise DomainError("Tables not found", 404)
        for table in tables:
            items = await self.products.find({"tableId": str(table["_id"])}).to_list()
            table["products"] = [{"id": str(i["_id"]), "name": i["name"], "price": i["price"], "qty": i["qty"]} for i in items]
            table["hasActiveOrder"] = bool(items)
            table["itemCount"] = sum(item["qty"] for item in items)
        return [public_document(i) or {} for i in tables]

    async def get(self, table_id):
        table = await self.tables.find_one({"_id": object_id(table_id, "table ID")})
        if not table: raise DomainError("Table not found", 404)
        items = await self.products.find({"tableId": table_id}).to_list()
        table["products"] = [{"id": str(i["_id"]), "name": i["name"], "price": i["price"], "qty": i["qty"]} for i in items]
        table["hasActiveOrder"] = bool(items)
        table["itemCount"] = sum(item["qty"] for item in items)
        return public_document(table) or {}

    async def delete(self, table_id):
        oid = object_id(table_id, "table ID")
        if not await self.tables.find_one({"_id": oid}): raise DomainError("Table not found", 404)
        await self.products.delete_many({"tableId": table_id}); await self.tables.delete_one({"_id": oid})

    async def reset(self, table_id):
        table = await self.tables.find_one({"_id": object_id(table_id, "table ID")})
        if not table: raise DomainError("Table not found", 404)
        await self.users.update_one({"_id": object_id(table["userId"], "user ID")}, {"$inc": {"totalAmount": table.get("billValue", 0)}})
        products = await self.products.find({"tableId": table_id}).to_list()
        now = datetime.now(timezone.utc)
        history = [{"adminId": table["userId"], "menuProductId": p.get("menuProductId"), "qty": p["qty"], "unitPriceCents": money_to_cents(p["price"]), "lineTotalCents": money_to_cents(p["price"]) * p["qty"], "currency": self.currency, "timeStamp": now, "userId": p.get("userId")} for p in products]
        if history: await self.history.insert_many(history)
        await self.tables.update_one({"_id": table["_id"]}, {"$set": {"billValue": 0}})
        await self.products.delete_many({"tableId": table_id})

    async def search(self, admin_id, name):
        query = {"userId": admin_id}
        if name: query["name"] = {"$regex": f"^{name}.*", "$options": "i"}
        tables = await self.tables.find(query).limit(5).to_list()
        if not tables: raise DomainError("Table not found", 404)
        return [{"id": str(i["_id"]), "name": i["name"], "capacity": i.get("capacity"), "billValue": i.get("billValue", 0), "products": []} for i in tables]


class MenuRepository:
    def __init__(self, database) -> None: self.users, self.menu = database["user"], database["menu"]

    async def add(self, data, admin_id):
        if not await self.users.find_one({"_id": object_id(admin_id, "admin ID"), "role": "admin"}): raise DomainError("Admin not found", 404)
        item = {"name": data["name"].lower(), "price": data["price"], "type": data["type"], "adminId": admin_id, "imageId": None, "imageUrl": None, "description": data["description"], "deleted": False}
        item["_id"] = (await self.menu.insert_one(item)).inserted_id
        return public_document(item) or {}

    async def list(self, admin_id, page, food_type=None, sort="name", direction="asc"):
        if page < 1: raise DomainError("Page must be positive", 400)
        if not await self.users.find_one({"_id": object_id(admin_id, "admin ID"), "role": "admin"}): raise DomainError("Admin not found", 404)
        if sort not in {"name", "price", "type"}: raise DomainError("Unsupported menu sort", 422)
        if direction not in {"asc", "desc"}: raise DomainError("Sort direction must be asc or desc", 422)
        query = {"adminId": admin_id, "deleted": False}
        if food_type: query["type"] = {"$regex": f"^{food_type}$", "$options": "i"}
        rows = await self.menu.find(query).sort(sort, 1 if direction == "asc" else -1).skip((page - 1) * 10).limit(10).to_list()
        return [public_document(i) or {} for i in rows]

    async def delete(self, product_id):
        result = await self.menu.update_one({"_id": object_id(product_id, "product ID")}, {"$set": {"deleted": True}})
        if not result.matched_count: raise DomainError("Product not found", 404)

    async def update(self, product_id, data):
        result = await self.menu.update_one({"_id": object_id(product_id, "product ID")}, {"$set": data})
        if not result.matched_count: raise DomainError("Product not found", 404)

    async def search(self, admin_id, name, food_type=None, sort="name", direction="asc"):
        if sort not in {"name", "price", "type"}: raise DomainError("Unsupported menu sort", 422)
        if direction not in {"asc", "desc"}: raise DomainError("Sort direction must be asc or desc", 422)
        query = {"adminId": admin_id, "deleted": False, "name": {"$regex": name, "$options": "i"}}
        if food_type: query["type"] = {"$regex": f"^{food_type}$", "$options": "i"}
        items = await self.menu.find(query).sort(sort, 1 if direction == "asc" else -1).limit(20).to_list()
        return [public_document(i) or {} for i in items]


class ProductRepository:
    def __init__(self, database) -> None: self.tables, self.products, self.users, self.employers = database["table"], database["products"], database["user"], database["employers"]

    async def add(self, data, employee_id):
        table = await self.tables.find_one({"_id": object_id(data["table_id"], "table ID")})
        if not table: raise DomainError("Table not found", 404)
        item = {"name": data["name"], "price": data["price"], "qty": data["qty"], "tableId": data["table_id"], "menuProductId": data["menu_product_id"], "userId": employee_id}
        item["_id"] = (await self.products.insert_one(item)).inserted_id
        await self.tables.update_one({"_id": table["_id"]}, {"$inc": {"billValue": data["price"] * data["qty"]}})
        employee = await self.users.find_one({"_id": object_id(employee_id, "employee ID")})
        if employee: await self.employers.update_one({"email": employee.get("email")}, {"$inc": {"income": data["price"] * data["qty"]}})
        return public_document(item) or {}

    async def delete(self, product_id):
        item = await self.products.find_one({"_id": object_id(product_id, "product ID")})
        if not item: raise DomainError("There is no product with this id", 404)
        total = item["price"] * item["qty"]
        await self.tables.update_one({"_id": object_id(item["tableId"], "table ID")}, {"$inc": {"billValue": -total}})
        employee = await self.users.find_one({"_id": object_id(item["userId"], "employee ID")})
        if employee: await self.employers.update_one({"email": employee.get("email")}, {"$inc": {"income": -total}})
        await self.products.delete_one({"_id": item["_id"]})


class ReservationRepository:
    def __init__(self, database) -> None: self.tables, self.reservations = database["table"], database["reservation"]
    async def create(self, table_id, data):
        if not await self.tables.find_one({"_id": object_id(table_id, "table ID")}): raise DomainError("Table not found", 404)
        item = {**data, "tableId": table_id}; item["_id"] = (await self.reservations.insert_one(item)).inserted_id
        return public_document(item) or {}
    async def for_table(self, table_id):
        if not await self.tables.find_one({"_id": object_id(table_id, "table ID")}): raise DomainError("Table not found", 404)
        return [public_document(i) or {} for i in await self.reservations.find({"tableId": table_id}).to_list()]
    async def update(self, table_id, reservation_id, data):
        result = await self.reservations.update_one({"_id": object_id(reservation_id, "reservation ID"), "tableId": table_id}, {"$set": data})
        if not result.matched_count: raise DomainError("Reservation not found", 404)
    async def delete(self, table_id, reservation_id):
        result = await self.reservations.delete_one({"_id": object_id(reservation_id, "reservation ID"), "tableId": table_id})
        if not result.deleted_count: raise DomainError("Reservation not found", 404)


class FoodTypeRepository:
    def __init__(self, database) -> None: self.collection = database["foodType"]
    async def create(self, data):
        item = dict(data); item["_id"] = (await self.collection.insert_one(item)).inserted_id
        return public_document(item) or {}
    async def list(self): return [public_document(i) or {} for i in await self.collection.find().to_list()]
