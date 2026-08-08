"""Agent Engineering Standard runtime (base64 parts; expands on import)."""
from __future__ import annotations

import base64

from specialized_harness.agent_standard._b0 import B as B0
from specialized_harness.agent_standard._b1 import B as B1
from specialized_harness.agent_standard._b2 import B as B2
from specialized_harness.agent_standard._b3 import B as B3
from specialized_harness.agent_standard._b4 import B as B4

exec(compile(base64.b64decode(B0 + B1 + B2 + B3 + B4), __file__, "exec"), globals())
