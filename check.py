#!/usr/bin/env python3
"""Re-decrypt each claimed break and print the result.

    python3 check.py            # both claims
    python3 check.py mvueh-1941 # one of them

No dependencies beyond the standard library.
"""

from __future__ import annotations

import json
import pathlib
import sys
import textwrap

from verifiers import adfgvx
from verifiers.enigma import Enigma

DATA = pathlib.Path(__file__).resolve().parent / "data"


def run(claim: dict) -> tuple[str, bool]:
    if claim["cipher"] == "Enigma I":
        key = claim["key"]
        machine = Enigma(
            rotors=tuple(key["rotors"]),
            rings=key["rings"],
            plugboard=key["plugboard"],
            reflector=key["reflector"],
        )
        indicator = claim["indicator"]
        window = machine(indicator["enciphered_key"], indicator["window"])
        if window != indicator["expected_body_window"]:
            return f"indicator gives {window}, claim says {indicator['expected_body_window']}", False
        plaintext = machine(claim["ciphertext"], window)
    else:
        plaintext = adfgvx.decrypt(
            claim["ciphertext"], claim["key"]["keyword"], claim["key"]["square"]
        )
    return plaintext, plaintext == claim["expected_plaintext"]


def main(argv: list[str]) -> int:
    wanted = set(argv[1:])
    failures = 0
    for path in sorted(DATA.glob("*.json")):
        claim = json.loads(path.read_text())
        if wanted and claim["id"] not in wanted:
            continue
        plaintext, agrees = run(claim)
        print(f"\n{claim['id']}: {claim['message']}")
        print(f"  claimed by {claim['claim']['by']}, {claim['claim']['dated']}")
        print(f"  ciphertext from {claim['ciphertext_source']['held_by']}")
        for line in textwrap.wrap(plaintext, 72):
            print(f"  {line}")
        print(f"  -> {claim['english']}")
        print("  matches the claim" if agrees else "  DOES NOT MATCH the claim")
        failures += not agrees
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
