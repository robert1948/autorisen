import subprocess
import pathlib
import shutil


def test_devlog_insertion(tmp_path):
    script_src = pathlib.Path("scripts/devlog_update.py")
    log_src = pathlib.Path("docs/DEVELOPMENT_LOG.md")
    work = tmp_path
    (work / "scripts").mkdir()
    (work / "docs").mkdir()
    shutil.copy(script_src, work / "scripts" / "devlog_update.py")
    (work / "docs" / "DEVELOPMENT_LOG.md").write_text(
        "# Autorisen – Development Log\n\n"
    )
    cmd = [
        "python",
        "scripts/devlog_update.py",
        "--type",
        "refactor",
        "--summary",
        "test entry",
    ]
    res = subprocess.run(cmd, cwd=work, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    content = (work / "docs" / "DEVELOPMENT_LOG.md").read_text()
    assert "test entry" in content
