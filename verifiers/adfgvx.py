"""ADFGVX decryption, written to check other people's claimed keys.

The cipher has two stages. A 6x6 square rewrites each plaintext character as
a pair of letters drawn from ADFGVX. Those pairs are written row-wise under a
keyword and read off column by column, the columns taken in the alphabetical
order of the keyword's letters.

Decryption undoes the columnar transposition first, then the square.
"""

from __future__ import annotations

HEADINGS = "ADFGVX"


def key_order(keyword: str) -> list[int]:
    """Column positions in the order their letters are read off.

    Repeated letters keep their left-to-right order, which is how the 1918
    key sheets number them.
    """
    return sorted(range(len(keyword)), key=lambda i: (keyword[i], i))


def undo_transposition(ciphertext: str, keyword: str) -> str:
    """Return the pairs in their original row-wise order."""
    width = len(keyword)
    if len(ciphertext) % 2:
        raise ValueError("ADFGVX text has an even number of letters")

    full, remainder = divmod(len(ciphertext), width)
    # Columns are read off in key order, but their lengths follow the
    # positions they were written at: the leftmost `remainder` columns carry
    # one extra character.
    lengths = [full + 1 if pos < remainder else full for pos in range(width)]

    columns: dict[int, str] = {}
    cut = 0
    for pos in key_order(keyword):
        columns[pos] = ciphertext[cut : cut + lengths[pos]]
        cut += lengths[pos]

    rows = max(lengths)
    return "".join(
        columns[pos][row]
        for row in range(rows)
        for pos in range(width)
        if row < lengths[pos]
    )


def decrypt(ciphertext: str, keyword: str, square: list[str]) -> str:
    """Decrypt `ciphertext` under a transposition `keyword` and 6x6 `square`."""
    ciphertext = "".join(ciphertext.split()).upper()
    if set(ciphertext) - set(HEADINGS):
        raise ValueError("ciphertext may only contain the letters ADFGVX")
    if len(square) != 6 or any(len(row) != 6 for row in square):
        raise ValueError("square must be 6x6")

    pairs = undo_transposition(ciphertext, keyword.upper())
    return "".join(
        square[HEADINGS.index(pairs[i])][HEADINGS.index(pairs[i + 1])]
        for i in range(0, len(pairs), 2)
    )
