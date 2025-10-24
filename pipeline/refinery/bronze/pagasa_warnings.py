import hashlib, json

from pipeline.asset import asset
from pipeline.config.api import pagasa
from pipeline.utils.extract_http import extract_http
from pipeline.utils.grammar import s

@asset(
    name="pagasa_warnings",
    stage="bronze",
    schema="""
        source_id VARCHAR PRIMARY KEY,
        hazard VARCHAR,
        payload JSON,
        inserted_at TIMESTAMP
    """,
    # Note: The @asset decorator automatically sets `inserted_at`
    dedupe_key="source_id",
    retry=1
)
def pagasa_warnings(ctx):
    """
    Extracts and loads the latest active hazard warnings from PAGASA's API
    and stores each top-level hazard type (e.g., "General Flood Advisory",
    "Tropical Storm Ramil", "Tropical Depression Salome") as a separate record
    in the `pagasa_warnings` bronze table.
    """

    data = extract_http("POST",
        pagasa.ACTIVE_WARNING_ENDPOINT,
        headers=pagasa.ACTIVE_WARNING_HEADERS,
    )

    # Split top-level hazards into separate records
    records = []
    for hazard, payload in data.items():
        payload = json.dumps(payload, sort_keys=True)
        records.append({
            "source_id": hashlib.sha256(
				f"{hazard}{payload}".encode()
			).hexdigest(),
            "hazard": hazard,
            "payload": payload,
        })
        
    # Debugging summary
    rows = len(records)
    ctx.log(f"✅ Parsed {rows} hazard payload{s(rows)}:\n")
    for h in records:
        print(f"🔹 {h['hazard']}")
        print(f"   → Hash: {h['source_id'][:8]}...")
        print(f"   → Size: {len(h['payload'])} bytes\n")
        
    return records