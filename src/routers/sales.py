"""
CASSERISISSIMA 2.0 — Router: Ventas
POST /api/v1/sales           — registrar cierre del día
GET  /api/v1/sales/summary   — resumen de ventas recientes
"""
import logging
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from db.database import get_db
from db.models import SaleTransaction, Product
from db.seed import get_active_scenario

router = APIRouter()
logger = logging.getLogger(__name__)


class SaleEntryItem(BaseModel):
    product_id: str
    quantity_sold: float = Field(ge=0.0, le=10.0)
    price_override: Optional[float] = Field(None, ge=0.0)


class DailySaleRequest(BaseModel):
    sale_date: Optional[str] = None  # ISO: "2026-05-22" — si None usa hoy
    items: list[SaleEntryItem]


@router.post("/sales")
def register_daily_sales(req: DailySaleRequest, db: Session = Depends(get_db)):
    """
    Registra el cierre del día para los productos vendidos.
    Solo registra productos con qty > 0.
    """
    scenario_id = get_active_scenario(db)
    sale_date = date.fromisoformat(req.sale_date) if req.sale_date else date.today()
    registered = []
    skipped = []

    for item in req.items:
        if item.quantity_sold <= 0:
            skipped.append(item.product_id)
            continue

        # Verificar que el producto existe
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        if not prod:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado.")

        price = item.price_override if (item.price_override is not None) else prod.selling_price
        revenue = round(item.quantity_sold * price, 2)

        # Upsert: si ya existe, actualiza
        existing = (
            db.query(SaleTransaction)
            .filter(
                SaleTransaction.scenario_id == scenario_id,
                SaleTransaction.product_id == item.product_id,
                SaleTransaction.sale_date == sale_date,
            )
            .first()
        )
        if existing:
            existing.quantity_sold = item.quantity_sold
            existing.revenue       = revenue
        else:
            txn = SaleTransaction(
                scenario_id=scenario_id,
                product_id=item.product_id,
                sale_date=sale_date,
                quantity_sold=item.quantity_sold,
                revenue=revenue,
                day_of_week=sale_date.weekday(),
                is_holiday=False,
                is_payday=sale_date.day in {14, 15, 28, 29, 30, 31},
            )
            db.add(txn)

        registered.append({"product_id": item.product_id, "qty": item.quantity_sold, "revenue": revenue})

    db.commit()
    total_revenue = sum(r["revenue"] for r in registered)
    total_units   = sum(r["qty"] for r in registered)

    logger.info(f"[Sales] Registradas {len(registered)} ventas del {sale_date} en escenario {scenario_id}")
    return {
        "status":        "ok",
        "sale_date":     sale_date.isoformat(),
        "scenario_id":   scenario_id,
        "total_units":   round(total_units, 1),
        "total_revenue": round(total_revenue, 2),
        "items_saved":   len(registered),
        "items_skipped": len(skipped),
    }


@router.get("/sales/recent")
def get_recent_sales(
    days: int = 7,
    db: Session = Depends(get_db),
):
    """Últimas N días de ventas por producto del escenario activo."""
    scenario_id = get_active_scenario(db)
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            SaleTransaction.sale_date,
            Product.name.label("product_name"),
            Product.category,
            SaleTransaction.quantity_sold,
            SaleTransaction.revenue,
        )
        .join(Product, Product.id == SaleTransaction.product_id)
        .filter(
            SaleTransaction.scenario_id == scenario_id,
            SaleTransaction.sale_date >= since,
        )
        .order_by(desc(SaleTransaction.sale_date), desc(SaleTransaction.quantity_sold))
        .all()
    )

    return {
        "scenario_id": scenario_id,
        "days": days,
        "sales": [
            {
                "sale_date":    r.sale_date.isoformat(),
                "product_name": r.product_name,
                "category":     r.category,
                "quantity":     round(r.quantity_sold, 1),
                "revenue":      round(r.revenue, 2),
            }
            for r in rows if r.quantity_sold > 0
        ],
    }


from fastapi.responses import StreamingResponse
from core.utils.excel_generator import generate_sales_excel

class SaleUpdateItem(BaseModel):
    product_id: str
    quantity_sold: float = Field(ge=0.0)

class ClosureUpdateRequest(BaseModel):
    items: list[SaleUpdateItem]


@router.get("/sales/closures")
def get_all_closures(db: Session = Depends(get_db)):
    """Obtiene el listado agrupado por fecha de todos los cierres registrados en el escenario activo."""
    scenario_id = get_active_scenario(db)
    
    rows = (
        db.query(
            SaleTransaction.sale_date,
            func.sum(SaleTransaction.revenue).label("total_revenue"),
            func.sum(SaleTransaction.quantity_sold).label("total_units"),
            func.count(SaleTransaction.id).label("items_count"),
        )
        .filter(SaleTransaction.scenario_id == scenario_id)
        .group_by(SaleTransaction.sale_date)
        .order_by(desc(SaleTransaction.sale_date))
        .all()
    )
    
    return {
        "scenario_id": scenario_id,
        "closures": [
            {
                "sale_date": r.sale_date.isoformat(),
                "total_revenue": round(r.total_revenue, 2),
                "total_units": round(r.total_units, 1),
                "items_count": r.items_count,
            }
            for r in rows
        ],
    }


@router.get("/sales/closures/{sale_date}")
def get_closure_details(sale_date: str, db: Session = Depends(get_db)):
    """Obtiene las transacciones detalladas de una fecha especifica, incluyendo todos los productos del catalogo."""
    scenario_id = get_active_scenario(db)
    try:
        parsed_date = date.fromisoformat(sale_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha invalido. Use AAAA-MM-DD.")
        
    txns = (
        db.query(SaleTransaction)
        .filter(
            SaleTransaction.scenario_id == scenario_id,
            SaleTransaction.sale_date == parsed_date,
        )
        .all()
    )
    txn_map = {t.product_id: t for t in txns}
    
    products = db.query(Product).filter(Product.is_active == True).all()
    
    details = []
    for p in products:
        txn = txn_map.get(p.id)
        qty = txn.quantity_sold if txn else 0.0
        rev = txn.revenue if txn else 0.0
        details.append({
            "product_id": p.id,
            "product_name": p.name,
            "category": p.category,
            "unit_price": p.selling_price,
            "quantity_sold": qty,
            "revenue": rev,
            "exists_in_db": txn is not None
        })
        
    return {
        "sale_date": sale_date,
        "scenario_id": scenario_id,
        "items": details,
    }


@router.put("/sales/closures/{sale_date}")
def update_closure(sale_date: str, req: ClosureUpdateRequest, db: Session = Depends(get_db)):
    """Guarda/actualiza las ventas de una fecha. Si la cantidad es 0, elimina la transaccion."""
    scenario_id = get_active_scenario(db)
    try:
        parsed_date = date.fromisoformat(sale_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha invalido. Use AAAA-MM-DD.")
        
    updated_count = 0
    deleted_count = 0
    inserted_count = 0
    
    for item in req.items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        if not prod:
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado.")
            
        existing = (
            db.query(SaleTransaction)
            .filter(
                SaleTransaction.scenario_id == scenario_id,
                SaleTransaction.product_id == item.product_id,
                SaleTransaction.sale_date == parsed_date,
            )
            .first()
        )
        
        if item.quantity_sold <= 0:
            if existing:
                db.delete(existing)
                deleted_count += 1
        else:
            revenue = round(item.quantity_sold * prod.selling_price, 2)
            if existing:
                existing.quantity_sold = item.quantity_sold
                existing.revenue = revenue
                updated_count += 1
            else:
                txn = SaleTransaction(
                    scenario_id=scenario_id,
                    product_id=item.product_id,
                    sale_date=parsed_date,
                    quantity_sold=item.quantity_sold,
                    revenue=revenue,
                    day_of_week=parsed_date.weekday(),
                    is_holiday=False,
                    is_payday=parsed_date.day in {14, 15, 28, 29, 30, 31},
                )
                db.add(txn)
                inserted_count += 1
                
    db.commit()
    
    totals = (
        db.query(func.sum(SaleTransaction.revenue), func.sum(SaleTransaction.quantity_sold))
        .filter(
            SaleTransaction.scenario_id == scenario_id,
            SaleTransaction.sale_date == parsed_date
        )
        .first()
    )
    
    total_revenue = totals[0] if totals and totals[0] is not None else 0.0
    total_units = totals[1] if totals and totals[1] is not None else 0.0
    
    return {
        "status": "ok",
        "sale_date": sale_date,
        "scenario_id": scenario_id,
        "inserted": inserted_count,
        "updated": updated_count,
        "deleted": deleted_count,
        "total_revenue": round(total_revenue, 2),
        "total_units": round(total_units, 1)
    }


@router.get("/sales/export")
def export_closures(db: Session = Depends(get_db)):
    """Exporta el resumen de cierres y detalle de ventas en formato Excel."""
    scenario_id = get_active_scenario(db)
    
    try:
        excel_stream = generate_sales_excel(db, scenario_id)
        
        filename = f"reporte_ventas_escenario_{scenario_id}_{date.today().isoformat()}.xlsx"
        
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        
        return StreamingResponse(
            excel_stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers
        )
    except Exception as e:
        logger.error(f"Error al exportar Excel: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al generar el reporte Excel.")
