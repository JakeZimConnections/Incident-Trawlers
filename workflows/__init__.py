# Registry of every workflow by name, so main.py can list and run them without knowing each one.
from . import default, zim_incident

# Every workflow main.py can run, by name. Add new ones here.
WORKFLOWS = {w.name: w for w in [default.WORKFLOW, zim_incident.WORKFLOW]}
