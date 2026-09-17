# cipher-break-verification

Independent re-checks of AI-assisted historical cipher breaks. Two so far, both
from September 2026: the 1941 Enigma message **MVUEH** and an unsolved 1918
**ADFGVX** radio message.

Neither check uses any of the solvers' code. Each starts from the ciphertext as
published by the archive that holds it, applies the claimed key with a
simulator written here, and prints what comes out.

```console
$ python3 check.py
mvueh-1941: German Army message Nr. 172, 10 July 1941, identifier MVUEH
  claimed by Carter Leffen, with GPT-6 Astra and parallel agents, 2026-09-14
  ciphertext from Frode Weierud's CryptoCellar archive, not the solver
  BRCEUZANGAKEDESMARSVWEGESXFEFINDEMIQINXROSTNOWROSENOWXSOFORTFUNKANTWORTX
  WASCHBBPCH
  -> Please give the route of march. I am in Rosenow, Rosenow. Reply by radio at once.
  matches the claim
```

Python 3.10 or later, no dependencies. `pip install pytest && python3 -m pytest`
runs the checks as tests.

## Why bother

A cipher break is one of the few AI results an outsider can settle on their
own. The key is a few dozen characters, the verifier is thirty lines, and the
input sits in someone else's archive. A wrong key produces noise, so no
calibrated reviewer is needed to see the difference. Most AI research claims
have none of these properties.

So these two are worth checking precisely because checking is cheap, and worth
writing down because the checks say different things about the two claims.

## MVUEH, 10 July 1941

German Army message Nr. 172, 82 letters, indicator GTA/KCI. It sat unbroken in
the Sullivan–Weierud corpus: short, on a key separate from that day's daily key
for the SS-Totenkopf division's supply service, and with a left-wheel turnover
in the middle.

[Carter Leffen broke it](https://mvueh-enigma-solved.carterl.chatgpt.site/) on
14–15 September 2026 using GPT-6 Astra with parallel agents. Rotors II–V–III,
reflector B, rings HMF, plugboard AC BE DG FH KN MO PR SU TV XZ.

What the check finds:

- `KCI` typed at window `GTA` gives `RWD`, the claimed body start.
- The archive's **unchanged** published ciphertext then gives connected
  German, garbled in 8 of 82 positions: `…MARSVWEGESXFEFINDEMIQINXROSTNOW
  ROSENOWXSOFORTFUNKANTWORTX…`
- Change one ring setting and both `ROSENOW` and `SOFORTFUNKANTWORT` vanish.

Note what does *not* count as evidence. Enigma is its own inverse, so the
plaintext re-enciphers to the ciphertext under **any** key. `test_mvueh_reencrypts`
is in the suite to make the point: it passes for every candidate and therefore
discriminates nothing. The evidence is the German, and the fact that the crib
which found the key (`ROSENOWROSENOW`, borrowed from the related SIPVX message)
fixed only 14 of 82 letters. The other 68 were free to be noise and are not.

The solver also publishes a "preferred" ciphertext that reads more cleanly,
built by choosing among letter alternatives recorded before the search for 12
faint positions in the handwritten original. That reading is partly fitted, so
this repo checks the unfitted one.

CryptoCellar now [marks the message broken](https://cryptocellar.org/bgac/g-army-july-1941.html),
which is the acceptance that matters: the corpus's custodian, not the solver.

## ADFGVX, 27 November 1918

One of the dozen-odd unsolved messages in the WWI ADFGVX corpus preserved by
J. Rives Childs (p. 217). Most of that corpus was read in 1918 by hand and the
rest by [Lasry and Niebel](https://www.tandfonline.com/doi/abs/10.1080/01611194.2016.1169461)
with hill-climbing. [prinz reports](https://www.prinzai.com/p/gpt-6-astra-solves-a-wwi-german-radio)
that GPT-6 Astra read this one on 17 September 2026 under the key
`TRUPPENVERSCHIEBUNG`.

The check gives:

```
EINENGLISCHERKREUZEREINLIEGXSEWASTOPOLXS4STENXEINGESCHWADERDERXALLIIERTENFOLGT26STENX
```

"An English cruiser docked at Sevastopol on the 24th. An allied squadron
follows on the 26th." The 170 characters split into eighteen columns of 9 and
one of 8, exactly as a 19-letter key requires.

Two details are worth keeping:

- **An outside record settles an ambiguous cell.** The square's scan carries
  handwritten corrections, and one cell reads as either 4 or 8. Our first pass
  chose 8 and got `S8STEN`; HMS Canterbury's log puts the ship at Sevastopol on
  the 24th, so the cell is 4 and its partner is 8. One character moves, and
  nothing else does — `test_the_ambiguous_square_cell_changes_one_character`
  pins that.
- **The German corrected our transcription.** We first read the square's `O`
  and `0` cells the wrong way round, which turned `SEWASTOPOL` into
  `SEWAST0P0L`. The plaintext made the error obvious. A transcription slip
  shows up locally in the output, which is a weak but real check on our own
  reading of the scans.

This claim is weaker than MVUEH on provenance, though not on arithmetic:

- Novelty rests on the author's "to my knowledge," and no custodian has marked
  the message solved.
- `TRUPPENVERSCHIEBUNG` is documented as in use from 9 December 1918, twelve
  days *after* this message's date. The post flags the discrepancy and does not
  resolve it. Either the recorded key period or the date is wrong.

The decryption is checkable while its provenance is not. Those are separate
questions and this repo answers only the first.

## Test vectors

Neither claim ships a test vector, so the ADFGVX implementation is also
checked against a worked example by a third party: Anil Andro's Spanish
history of Painvin and the 1918 ciphers encrypts `SE ESPERA ATAQUE
INMINENTE` under the key `GEORGEORWELL`, by hand, with every intermediate
grid printed
([archived page](https://web.archive.org/web/20210212215335/https://sites.google.com/site/anilandro/06120-adfgx-01)).

That example is worth more than its size suggests. Its last row is short, so
it exercises the one rule the 1918 message actually depends on: which columns
carry the extra character. Get that wrong and the digraphs shift, and no key
will ever read. It is also ADFGX, the 5x5 version, so supporting it keeps the
square size a parameter rather than an assumption.

## What is not checked here

- MVUEH's 43,016-batch search, its SAT cross-check, and its competing-key
  audit. Uniqueness among the 923 indicator-compatible keys is the solver's
  claim, not ours.
- Whether either message was previously read by someone else.
- The historical readings: which Rosenow, "Waschbusch" as a signature, the
  retransmission link to SIPVX, and the Canterbury log itself, which we take
  from prinz's post rather than from the original.
- The ADFGVX ciphertext and square were transcribed by eye from page scans in
  the post. Nobody has compared our transcription against Childs directly.
- "Connected German" is our own reading, not a German specialist's.

## Layout

    verifiers/enigma.py   Enigma I: rotors I-V, reflectors B and C, plugboard
    verifiers/adfgvx.py   ADFGX and ADFGVX: columnar transposition and square
    data/*.json           one claim per file: key, ciphertext, source, expected text
    tests/test_claims.py  the checks, including the ones that must fail
    check.py              run everything and print the plaintext

Adding a claim means adding a JSON file and, if it uses a cipher not here yet,
a verifier beside the other two.

## Sources

- Leffen's exhibit and [completion report](https://mvueh-enigma-solved.carterl.chatgpt.site/downloads/completion-report.md)
- [CryptoCellar, German Army messages, July 1941](https://cryptocellar.org/bgac/g-army-july-1941.html)
- [prinz, "GPT-6 Astra Solves a WWI German Radio Cipher"](https://www.prinzai.com/p/gpt-6-astra-solves-a-wwi-german-radio)
- [Crypto Museum, Enigma wiring](https://www.cryptomuseum.com/crypto/enigma/wiring.htm)
- Lasry and Niebel, "Deciphering ADFGVX messages from the Eastern Front of World War I," *Cryptologia* 41(2), 2017
