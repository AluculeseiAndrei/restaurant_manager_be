from restaurant_api.repositories.employees import AsyncEmployeeRepository


class EmployeeService:
    def __init__(self, repository: AsyncEmployeeRepository) -> None:
        self.repository = repository

    async def create(self, data): return await self.repository.create(data)
    async def list(self, restaurant_id): return await self.repository.list(restaurant_id)
    async def get(self, restaurant_id, employee_id): return await self.repository.get(restaurant_id, employee_id)
    async def delete(self, restaurant_id, employee_id): return await self.repository.delete(restaurant_id, employee_id)
    async def update(self, restaurant_id, employee_id, data): return await self.repository.update(restaurant_id, employee_id, data)
    async def income(self, restaurant_id, employee_id, value): return await self.repository.income(restaurant_id, employee_id, value)
    async def by_email(self, email): return await self.repository.by_email(email)
