from typing import Dict

# In-memory stores
progress_store: Dict[str, Dict[str, int]] = {}
data_store: Dict[str, Dict] = {}
current_task_id = ""
