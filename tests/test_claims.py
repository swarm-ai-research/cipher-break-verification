"""Re-check each claimed key against the archive's own ciphertext."""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from verifiers import adfgvx  # noqa: E402
from verifiers.enigma import Enigma  # noqa: E402

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"
MVUEH = json.loads((DATA / "mvueh-1941.json").read_text())
ADFGVX = json.loads((DATA / "adfgvx-1918.json").read_text())


def machine() -> Enigma:
    key = MVUEH["key"]
    return Enigma(
        rotors=tuple(key["rotors"]),
        rings=key["rings"],
        plugboard=key["plugboard"],
        reflector=key["reflector"],
    )


def test_mvueh_indicator_gives_the_claimed_body_window():
    indicator = MVUEH["indicator"]
    assert (
        machine()(indicator["enciphered_key"], indicator["window"])
        == indicator["expected_body_window"]
    )


def test_mvueh_body_decrypts_to_german():
    plaintext = machine()(MVUEH["ciphertext"], MVUEH["indicator"]["expected_body_window"])
    assert plaintext == MVUEH["expected_plaintext"]
    # The phrases that carry the message, none of them supplied by the crib
    # that found the key.
    for phrase in ("ANGA", "DESMARS", "EFINDEMIQINX", "ROSENOW", "SOFORTFUNKANTWORT"):
        assert phrase in plaintext


def test_mvueh_reencrypts():
    """Enigma is self-inverse. This proves the arithmetic, not the key."""
    window = MVUEH["indicator"]["expected_body_window"]
    assert machine()(MVUEH["expected_plaintext"], window) == MVUEH["ciphertext"]


def test_mvueh_garbles_are_few():
    """The archive's unchanged text carries 8 garbled letters out of 82."""
    preferred = "BTTEUMANGABEDESMARSQWEGESXBEFINDEMIQINXROSENOWROSENOWXSOFORTFUNKANTWORTXWASCHBBSCH"
    received = MVUEH["expected_plaintext"]
    assert len(received) == len(preferred) == 82
    assert sum(a != b for a, b in zip(received, preferred)) == 8


@pytest.mark.parametrize("letter", ["A", "B", "Z"])
def test_a_wrong_ring_setting_destroys_the_german(letter: str):
    """The discriminating check is the language, so show a near miss failing."""
    key = MVUEH["key"]
    wrong = Enigma(
        rotors=tuple(key["rotors"]),
        rings=key["rings"][:2] + letter,
        plugboard=key["plugboard"],
        reflector=key["reflector"],
    )
    plaintext = wrong(MVUEH["ciphertext"], MVUEH["indicator"]["expected_body_window"])
    assert "SOFORTFUNKANTWORT" not in plaintext
    assert "ROSENOW" not in plaintext


def test_adfgvx_decrypts_to_german():
    plaintext = adfgvx.decrypt(
        ADFGVX["ciphertext"], ADFGVX["key"]["keyword"], ADFGVX["key"]["square"]
    )
    assert plaintext == ADFGVX["expected_plaintext"]
    for phrase in ("EINENGLISCHERKREUZER", "SEWASTOPOL", "ALLIIERTEN", "FOLGT26STEN"):
        assert phrase in plaintext


def test_adfgvx_column_lengths_follow_the_key():
    """170 characters under a 19-letter key: eighteen columns of 9, one of 8."""
    text = ADFGVX["ciphertext"]
    keyword = ADFGVX["key"]["keyword"]
    assert len(text) == 170 and len(keyword) == 19
    full, remainder = divmod(len(text), len(keyword))
    lengths = [full + 1 if i < remainder else full for i in range(len(keyword))]
    assert lengths.count(9) == 18 and lengths.count(8) == 1
    assert sorted(adfgvx.undo_transposition(text, keyword)) == sorted(text)


def test_the_ambiguous_square_cell_changes_one_character():
    """The scan's 4/8 cell. HMS Canterbury's log picks 4; nothing else moves."""
    other = list(ADFGVX["key"]["square"])
    other[0] = other[0].replace("4", "8")
    other[2] = other[2].replace("8", "4")
    flipped = adfgvx.decrypt(ADFGVX["ciphertext"], ADFGVX["key"]["keyword"], other)
    differences = [
        i for i, (a, b) in enumerate(zip(flipped, ADFGVX["expected_plaintext"])) if a != b
    ]
    assert differences == [40]
    assert flipped[39:45] == "S8STEN"


def test_a_wrong_adfgvx_keyword_destroys_the_german():
    wrong = adfgvx.decrypt(
        ADFGVX["ciphertext"], "TRUPPENVERSCHIEBUNX", ADFGVX["key"]["square"]
    )
    assert "SEWASTOPOL" not in wrong
