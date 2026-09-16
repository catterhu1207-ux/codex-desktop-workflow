"""26.908.9136.0: preserve qualified 4834 behavior; plan yellow precedes pinned red."""
from hotfix_profile_26908_4834 import *
PAIRS = dict(PAIRS)
PAIRS["plan_pending_yellow_indicator"] = tuple(
    (old, new.replace(b"e.i&&(e.p||n)?`danger`:e.p?`#eab308`:n?`info`:null", b"e.p?`#eab308`:e.i&&n?`danger`:n?`info`:null"))
    for old, new in PAIRS["plan_pending_yellow_indicator"]
)
SECONDARY_ENTRY_PATH = "webview/assets/app-primary-b36a719dba75.js"
SECONDARY_ENTRY_SOURCE_SHA256 = "255287957d4cf9a21d386948c997114bf039d5c15fc73258d3df5095114a047a"
