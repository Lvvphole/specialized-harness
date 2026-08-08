"""Agent Engineering Standard runtime (chunked plain source)."""
from __future__ import annotations

from specialized_harness.agent_standard._runtime_chunk_0 import CHUNK as C0
from specialized_harness.agent_standard._runtime_chunk_1 import CHUNK as C1
from specialized_harness.agent_standard._runtime_chunk_2 import CHUNK as C2

exec(compile(C0 + C1 + C2, __file__, "exec"), globals())
