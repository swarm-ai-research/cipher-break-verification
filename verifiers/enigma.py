"""Enigma I simulator, written to check other people's claimed keys.

Standard Army/Luftwaffe Enigma I: three rotors from I-V, reflector B or C,
identity entry wheel, plugboard. Ring settings and window positions are
letters; 'A' is 1 in the usual archival numbering.

Nothing here is borrowed from any solver's code. The wiring and turnover
notches are the published ones (Crypto Museum, "Enigma wiring").
"""

from __future__ import annotations

from dataclasses import dataclass

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ROTORS = {
    "I": ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),
    "II": ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
    "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
    "IV": ("ESOVPZJAYQUIRHXLNFTGKDCMWB", "J"),
    "V": ("VZBRGITYUPSDNHLXAWMJQOFECK", "Z"),
}

REFLECTORS = {
    "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}


def _plugboard(pairs: str) -> dict[str, str]:
    board = {c: c for c in ALPHABET}
    for pair in pairs.split():
        a, b = pair.upper()
        if board[a] != a or board[b] != b:
            raise ValueError(f"letter used twice in plugboard: {pair}")
        board[a], board[b] = b, a
    return board


@dataclass(frozen=True)
class Enigma:
    """A machine setting. `rotors` is left to right, as written in key sheets."""

    rotors: tuple[str, str, str]
    rings: str
    plugboard: str = ""
    reflector: str = "B"

    def __post_init__(self) -> None:
        if len(self.rotors) != 3 or any(r not in ROTORS for r in self.rotors):
            raise ValueError(f"need three rotors from {sorted(ROTORS)}")
        if len(set(self.rotors)) != 3:
            raise ValueError("a rotor cannot be fitted twice")
        if len(self.rings) != 3 or set(self.rings) - set(ALPHABET):
            raise ValueError("rings must be three letters")

    def __call__(self, text: str, window: str) -> str:
        """Encipher or decipher `text` with the wheels starting at `window`.

        Enigma is its own inverse, so this one method does both.
        """
        if len(window) != 3 or set(window) - set(ALPHABET):
            raise ValueError("window must be three letters")

        board = _plugboard(self.plugboard)
        wiring = [ROTORS[r][0] for r in self.rotors]
        notch = [ROTORS[r][1] for r in self.rotors]
        ring = [ALPHABET.index(c) for c in self.rings]
        pos = [ALPHABET.index(c) for c in window]
        reflector = REFLECTORS[self.reflector]

        out = []
        for letter in text:
            if letter not in ALPHABET:
                raise ValueError(f"not a cipher letter: {letter!r}")

            # Stepping happens before the lamp lights. The middle wheel steps
            # itself and the left one when it sits on its own notch: the
            # double step.
            if ALPHABET[pos[1]] == notch[1]:
                pos[0] = (pos[0] + 1) % 26
                pos[1] = (pos[1] + 1) % 26
            elif ALPHABET[pos[2]] == notch[2]:
                pos[1] = (pos[1] + 1) % 26
            pos[2] = (pos[2] + 1) % 26

            c = ALPHABET.index(board[letter])
            for i in (2, 1, 0):
                shift = pos[i] - ring[i]
                c = (ALPHABET.index(wiring[i][(c + shift) % 26]) - shift) % 26
            c = ALPHABET.index(reflector[c])
            for i in (0, 1, 2):
                shift = pos[i] - ring[i]
                c = (wiring[i].index(ALPHABET[(c + shift) % 26]) - shift) % 26
            out.append(board[ALPHABET[c]])
        return "".join(out)
