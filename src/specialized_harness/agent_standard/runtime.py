"""Agent Engineering Standard runtime (chunked plain source)."""
from __future__ import annotations

from specialized_harness.agent_standard._rt0 import CHUNK as C0
from specialized_harness.agent_standard._rt1 import CHUNK as C1
from specialized_harness.agent_standard._rt2 import CHUNK as C2
from specialized_harness.agent_standard._rt3 import CHUNK as C3
from specialized_harness.agent_standard._rt4 import CHUNK as C4

exec(compile(C0 + C1 + C2 + C3 + C4, __file__, "exec"), globals())
