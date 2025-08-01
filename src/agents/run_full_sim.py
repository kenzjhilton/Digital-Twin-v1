"""
run_full_sim.py
Simulates one end-to-end run (ore ➜ fertilizer ➜ export) with real data rows
from AMX MOTHER FILE 2.xlsx, using the Supply-chain-reconstruction agents.
"""

import pandas as pd
from SC_orchestrator import SupplyChainOrchestrator
from mining_agent          import MiningAgent
from processing_agent      import ProcessingAgent
from manufacturing_agent   import ManufacturingAgent
from distribution_agent    import DistributionAgent
from retail_agent          import RetailAgent
from datetime import datetime

# --------------------------------------------------------------------------------------
# 1) ── READ THE PRODUCTION & EXPORT SHEETS you already inspected -----------------------
# --------------------------------------------------------------------------------------
from pathlib import Path
HERE   = Path(__file__).resolve().parent       # -> src/agents
EXCEL  = HERE / "AMX MOTHER FILE 2.xlsx"       # full path object
xl     = pd.ExcelFile(EXCEL)                  # no FileNotFoundError
if not xl.sheet_names:
    raise ValueError(f"Excel file {EXCEL} has no sheets. Check the file path.")


# --- mining production row ("Production in P2O5 (Ktons)") -----------------------------
prod_df = (xl
           .parse(xl.sheet_names[0])
           .loc[lambda d: d.iloc[:, 0].astype(str)
                        .str.contains(r"Production\s+.*P2O5", case=False, na=False)]
           .squeeze())

production = []
for col in prod_df.index[2:]:            # skip the text columns
    try:
        yr = int(float(col))
    except (ValueError, TypeError):
        continue
    val = prod_df[col]
    if pd.notnull(val):
        production.append({"year": yr, "ore_tons": float(val) * 1_000})  # Ktons ➜ tons
production = sorted(production, key=lambda x: x["year"])  # chronological list

# --- export breakdown sheet -----------------------------------------------------------
exp_raw = xl.parse("break down export")
years = [int(c) for c in exp_raw.columns if str(c).isdigit()]
exports = []
cur_country = None
for _, row in exp_raw.iterrows():
    if pd.notnull(row.get("TRADITIONAL PRODUCTS")):
        cur_country = str(row["TRADITIONAL PRODUCTS"]).strip()
    product = str(row.get("Unnamed: 1", "")).strip()
    if product.lower() in {"product", "tons", "usd"} or not product:
        continue
    for y in years:
        tons = row[y]
        if pd.notnull(tons) and tons > 0:
            exports.append({"country": cur_country,
                            "product": product,
                            "year": int(y),
                            "tons": float(tons)})
# --------------------------------------------------------------------------------------
# 2) ── BUILD AGENTS with simple, Ma’aden-style parameters ------------------------------
# --------------------------------------------------------------------------------------
mine = MiningAgent("MINE_MPC1", "Maaden Phosphate Mine", 200_000,
                   ["Phosphorite Ore"], extraction_rate=10_000)

processing_recipes = {
    "Phosphorite_to_PG": {
        "input_material":       "Phosphorite Ore",
        "output_material":      "PG",            # phosphoric-acid grade
        "conversion_ratio":     0.82,
        "processing_time_hours": 3.0,
        "energy_cost_per_ton":  40.0,
        "required_method":      "chemical_processing"
    }
}
processor = ProcessingAgent("PROC_MPC1", "Phosphoric-acid Plant",
                            30_000, ["chemical_processing"], processing_recipes)

manufacturing_recipes = {
    "PG_to_Fertilizer": {
        "input_materials":      {"PG": 1.0, "additives": 0.05},
        "output_product":       "Bagged_Fertilizer",
        "output_quantity_ratio":0.92,
        "production_time_hours":2.0,
        "energy_cost_per_unit": 15.0,
        "required_line":        "chemical_production",
        "quality_requirements": {"min_purity": 0.85}
    }
}
manufacturer = ManufacturingAgent("MFG_MPC1", "DAP Fertilizer Plant",
                                  25_000, ["chemical_production"], manufacturing_recipes)

dist = DistributionAgent("DIST_MPC1", "Jubail Export Hub", 50_000,
                         ship_zones=["Zone_A", "Zone_B", "Zone_C"])
retail = RetailAgent("RTL_INTL1", "International Customers",
                     store_capacity=1_000_000,
                     sales_channels=["bulk_export"],
                     customer_zones=["industrial"])

# --------------------------------------------------------------------------------------
# 3) ── SET UP ORCHESTRATOR & ROUTING ---------------------------------------------------
# --------------------------------------------------------------------------------------
orch = SupplyChainOrchestrator()
orch.register_mining_agent(mine,                {"Phosphorite Ore": "PROC_MPC1"})
orch.register_processing_agent(processor,       {"PG":              "MFG_MPC1"})
orch.register_manufacturing_agent(manufacturer, {"Bagged_Fertilizer":"DIST_MPC1"})
orch.register_distribution_agent(dist,          retail_agent_id="RTL_INTL1")
orch.register_retail_agent(retail)

# --------------------------------------------------------------------------------------
# 4) ── LOOP THROUGH ONE YEAR OF PRODUCTION -------------------------------------------
#      (for a quick demo we’ll use the first row; you can iterate over all years)
# --------------------------------------------------------------------------------------
demo_year = production[0]          # pick 1st year for quick run
trace_id = orch.inject_raw_materials("MINE_MPC1", "Phosphorite Ore",
                                     demo_year["ore_tons"])

# ---- AUTO-HANDLE THE PROCESSING OPERATOR REQUEST -------------------------------------
req = orch.get_pending_operator_requests()[0]
inputs_proc = {"selected_recipe": "Phosphorite_to_PG",
               "processing_priority": "normal",
               "quality_target": 0.88,
               "batch_size": min(20_000, req["quantity"])}  # simple rule
orch.process_operator_request(req["request_id"], inputs_proc)

# ---- MANUFACTURING: pull PG from plant & convert -------------------------------------
# (Since orchestrator doesn’t yet auto-create a manufacturing request, we script it)
mfg_inputs_required = manufacturer.get_required_inputs("PG_to_Fertilizer",
                                                       quantity=20_000)
mfg_inputs = {k: v.get("default") for k, v in mfg_inputs_required.items()}
mfg_result = manufacturer.process_material("PG_to_Fertilizer", mfg_inputs)

# Immediately finish job for demo:
manufacturer.run_manufacturing_operations(hours=3)  # fast-forward 3h

# Ship fertilizer to distribution
manufacturer.create_shipment_to_distribution("Bagged_Fertilizer",
                                             mfg_result["expected_output_quantity"],
                                             "DIST_MPC1")
manufacturer.process_shipments()                # dispatch

# Distribution receives it
for ship in manufacturer.pending_product_shipments.values():
    pass  # not used here
received = dist.process_material("Bagged_Fertilizer",
                                 mfg_result["expected_output_quantity"])

# --------------------------------------------------------------------------------------
# 5) ── CREATE ONE EXPORT ORDER (using first row of exports dataframe) -----------------
# --------------------------------------------------------------------------------------
export = exports[0]
dist.create_shipping_order("Bagged_Fertilizer", export["tons"],
                           destination=export["country"],
                           delivery_zone="Zone_A")
dist.process_shipments()

# Retail receives shipment
for ship in dist.active_shipments.values():
    if ship["status"] == "dispatched":
        ship["status"] = "delivered"                     # instant delivery for demo
        retail.receive_shipment_from_distribution(ship)

# --------------------------------------------------------------------------------------
# 6) ── PRINT SUMMARY ------------------------------------------------------------------
# --------------------------------------------------------------------------------------
print("\n=== SYSTEM STATUS ===")
print(orch.get_system_status())
print("\n=== JOURNEY LOG ===")
for step in orch.get_material_trace(trace_id).journey_log:
    ts = step["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts:19} | {step['stage']:12} | {step['operation']:10} | "
          f"{step['agent_id']}")

print("\nRetail inventory snapshot:", retail.product_inventory)
