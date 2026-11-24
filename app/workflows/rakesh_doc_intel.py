# Rakesh doc intel workflow: walks doc_intel_inbox/, reads each file and reports its content type, read-only so it can't change the documents.
from app.core.langgraph import Workflow
from app.core.langgraph.tools import read_file
from app.schemas.graph import RAK_doc_intel_state

INBOX = "doc_intel_inbox"  # also the starting inbox_path, so prompt and state agree

# Survey every file in doc_intel_inbox/ and classify it, so files can later be routed to the right workflow.
# shortcut: read_file only reads text, so binary files (PDF, images, Office) are classified by name/extension; add a parser tool when those need real analysis.
WORKFLOW = Workflow(
    name="rakesh_doc_intel",
    state_schema=RAK_doc_intel_state,
    tools=[read_file],
    prompt=(
        f"Look in the folder {INBOX}. List every folder and file in it, "
        "going into each subfolder. Then read each file (skip .gitkeep) and work out "
        "what kind of content it holds. Reply with a folder tree, then a table with one "
        "row per file: path, file type, what the content is (e.g. incident report, "
        "invoice, log, contract, code), a one-line summary, and the workflow it should "
        "be processed by next. If a file can't be read, say so and classify it by its "
        "name and extension. If the folder is empty, say so."
    ),
    # shortcut: no tool writes documents/errors yet (ToolNode only writes messages), so they stay
    # empty and the answer is the only output; add a record_document tool returning Command(update=...) to fill them.
    initial_state={
        "inbox_path": INBOX,
        "documents": {},
        "errors": [],
    },
)
