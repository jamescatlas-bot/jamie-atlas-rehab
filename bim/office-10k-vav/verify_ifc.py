"""Validate the IFC against the IFC4 schema and rebuild every solid with the geometry kernel."""
import logging
import os
import sys

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.validate

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "Office-10k-VAV-Mechanical.ifc")
f = ifcopenshell.open(path)

logger = logging.getLogger("ifc-validate")
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())
ifcopenshell.validate.validate(f, logger, express_rules=False)
print("schema validation finished (any problems are listed above)")

settings = ifcopenshell.geom.settings()
ok = bad = 0
for p in f.by_type("IfcProduct"):
    if not p.Representation:
        continue
    try:
        ifcopenshell.geom.create_shape(settings, p)
        ok += 1
    except Exception as ex:  # noqa: BLE001
        bad += 1
        print("geometry failed:", p, ex)
print("geometry rebuilt for %d products, %d failures" % (ok, bad))
sys.exit(1 if bad else 0)
