from sqlalchemy import select
from database.connection import AsyncSessionLocal
from database.models import Product

async def list_products() -> dict:
    """Lista todos los productos activos en el catálogo de la pastelería."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product).where(Product.is_active == True))
        products = result.scalars().all()
        
        return {
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.selling_price
                } for p in products
            ]
        }
