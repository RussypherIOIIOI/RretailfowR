"""Print or apply the bounded, administrator-approved synthetic RetailFlow grants.

Printing a plan does not authorize it. Use --apply only after the owner approves
the exact plan. Never grants catalog-wide schema creation or touches old data.
"""

import argparse
from retailflow.config import Config
from scripts.databricks_cli import cli, save

PRINCIPAL = "e92b585c-22cc-4813-b00e-b894ea680a37"
COMMENT = "RetailFlow synthetic portfolio release 20261030"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--admin-profile", default="U2M")
    parser.add_argument("--catalog", default="tmc_solutions_jvs")
    parser.add_argument("--test-suffix", default="20261030a")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    configs = [Config(args.catalog), Config(args.catalog, "retailflow_test" + args.test_suffix)]
    schema_grants = ["USE_SCHEMA", "CREATE_TABLE", "SELECT", "MODIFY"]
    volume_grants = ["READ_VOLUME", "WRITE_VOLUME"]
    plan = {
        "principal": PRINCIPAL, "catalog": args.catalog, "catalog_grants_added": [],
        "schemas": [
            {"name": cfg.prefix + "_" + layer, "privileges": schema_grants}
            for cfg in configs for layer in ("bronze", "silver", "gold", "ops")
        ],
        "volumes": [
            {"name": f"{args.catalog}.{cfg.prefix}_bronze.fixtures", "privileges": volume_grants}
            for cfg in configs
        ],
    }
    save("evidence/release-20261030/permission-plan.json", plan)
    if not args.apply:
        print("Plan saved; no schemas, volumes or grants changed.")
        return
    existing = {item["name"]: item for item in cli(args.admin_profile, "schemas", "list", args.catalog)}
    # A resumed provisioning operation may reuse its own empty schemas only.
    for schema in plan["schemas"]:
        old = existing.get(schema["name"])
        if old and old.get("comment") != COMMENT:
            raise ValueError("Refusing to adopt an existing schema: " + schema["name"])
        if old and cli(args.admin_profile, "tables", "list", args.catalog, schema["name"]):
            raise ValueError("Provisioning expects empty schemas: " + schema["name"])
    results = []
    for schema in plan["schemas"]:
        name = schema["name"]
        if name not in existing:
            cli(args.admin_profile, "schemas", "create", name, args.catalog, "--comment", COMMENT)
        results.append(cli(args.admin_profile, "grants", "update", "schema", args.catalog + "." + name,
                           payload={"changes": [{"principal": PRINCIPAL, "add": schema_grants}]}))
    for cfg in configs:
        schema = cfg.prefix + "_bronze"
        volumes = cli(args.admin_profile, "volumes", "list", args.catalog, schema)
        if not any(volume["name"] == "fixtures" for volume in volumes):
            cli(args.admin_profile, "volumes", "create", args.catalog, schema, "fixtures", "MANAGED",
                "--comment", COMMENT)
        results.append(cli(args.admin_profile, "grants", "update", "volume",
                           args.catalog + "." + schema + ".fixtures",
                           payload={"changes": [{"principal": PRINCIPAL, "add": volume_grants}]}))
    save("evidence/release-20261030/permission-apply.json", {"plan": plan, "results": results})
    print("Scoped provisioning applied; inspect permission-apply.json.")


if __name__ == "__main__":
    main()
