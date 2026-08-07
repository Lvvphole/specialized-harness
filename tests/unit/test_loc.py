"""Net LOC measurement unit tests."""
from pathlib import Path
from specialized_harness.nodes.deterministic.loc import measure_net_loc, snapshot_text_files


def test_empty_diff_is_zero(tmp_path: Path):
    (tmp_path / "a.py").write_text("x = 1\n")
    base = snapshot_text_files(tmp_path)
    assert measure_net_loc(base, tmp_path) == 0


def test_new_file_counts_lines(tmp_path: Path):
    base = snapshot_text_files(tmp_path)
    (tmp_path / "new.py").write_text("a\nb\nc\n")
    assert measure_net_loc(base, tmp_path) == 3


def test_modified_file_counts_churn(tmp_path: Path):
    (tmp_path / "a.py").write_text("one\ntwo\n")
    base = snapshot_text_files(tmp_path)
    (tmp_path / "a.py").write_text("one\nthree\nfour\n")
    net = measure_net_loc(base, tmp_path)
    assert net >= 2
