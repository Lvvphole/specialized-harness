"""Agent Engineering Standard runtime (chunked plain source)."""
from __future__ import annotations

from specialized_harness.agent_standard._rt0 import CHUNK as C0
from specialized_harness.agent_standard._rt1 import CHUNK as C1
from specialized_harness.agent_standard._rt2 import CHUNK as C2
from specialized_harness.agent_standard._rt3 import CHUNK as C3
from specialized_harness.agent_standard._rt4 import CHUNK as C4
from specialized_harness.agent_standard._rt5 import CHUNK as C5
from specialized_harness.agent_standard._rt6 import CHUNK as C6
from specialized_harness.agent_standard._rt7 import CHUNK as C7
from specialized_harness.agent_standard._rt8 import CHUNK as C8

exec(compile(C0 + C1 + C2 + C3 + C4 + C5 + C6 + C7 + C8, __file__, "exec"), globals())
