"""The README's CLI example must show what the CLI actually prints."""

import json
import re
from pathlib import Path

from bd_trx_parser.__main__ import main

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")


def test_readme_cli_stdin_example_matches_real_output(monkeypatch, capsys):
    piped = re.search(r'echo "(?P<sms>[^"]+)" \| python -m bd_trx_parser', README)
    documented = re.search(r"Outputs formatted JSON:\s*```json\n(?P<json>.*?)```", README, re.S)
    assert piped and documented, "README CLI example not found"

    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(piped["sms"] + "\n"))
    assert main([]) == 0
    actual = json.loads(capsys.readouterr().out)
    expected = json.loads(documented["json"])

    # The hash is elided as "..." in the README.
    actual["transaction"]["hash"] = expected["transaction"]["hash"]
    assert actual == expected
