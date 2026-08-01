from fastmcp import FastMCP
from mcp_server.tools.products import list_products
from mcp_server.tools.inventory import check_inventory, get_rop_alerts
from mcp_server.tools.demand_forecast import predict_demand
from mcp_server.tools.newsvendor import calculate_optimal_production
from mcp_server.tools.scheduling import create_scheduled_job

# Instancia de FastMCP
mcp = FastMCP("Casserisissima")

# Registrar herramientas
mcp.tool()(list_products)
mcp.tool()(check_inventory)
mcp.tool()(get_rop_alerts)
mcp.tool()(predict_demand)
mcp.tool()(calculate_optimal_production)
mcp.tool()(create_scheduled_job)

if __name__ == "__main__":
    # Correr el servidor usando transporte SSE
    mcp.run(transport="sse", port=8000)
