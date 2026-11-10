# ZIM incident workflow: uses ZimState to gather Cognito, Stripe and Kibana evidence for an incident.
from core import Workflow
from state import ZimState
from tools import read_file, run_shell

# Investigate a ZIM incident. Cognito, Stripe and Kibana tools still to be added to tools/.
WORKFLOW = Workflow(
    name="zim_incident",
    state_schema=ZimState,
    tools=[read_file, run_shell],
    prompt=(
        "Investigate this ZIM incident. Gather the user's Cognito details, "
        "the Stripe payment reference and the relevant Kibana logs, "
        "then summarise what went wrong."
    ),
    initial_state={  # ZimState fields start empty
        "cognito_user": None,
        "stripe_ref": None,
        "kibana_logs": [],
    },
)
