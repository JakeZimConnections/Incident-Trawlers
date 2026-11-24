# Registry of every workflow by name, so the API can list and run them without knowing each one.
from . import default, rakesh_doc_intel, zim_incident

# Every workflow the API can run, by name. Add new ones here.
WORKFLOWS = {w.name: w for w in [default.WORKFLOW, zim_incident.WORKFLOW, rakesh_doc_intel.WORKFLOW]}
