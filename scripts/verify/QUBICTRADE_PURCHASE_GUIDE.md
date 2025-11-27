# QubicTrade GENESIS Asset Purchase Guide

## Vorbereitung

### Schritt 1: Seeds vorbereiten
Öffne `scripts/verify/qubictrade_helper.py` und kopiere alle 8 Seeds in eine Textdatei für schnellen Zugriff.

### Schritt 2: 8 Browser-Tabs öffnen
Öffne QubicTrade in 8 separaten Browser-Tabs (oder 8 Browser-Fenstern).

## Kauf-Reihenfolge

### Empfohlene Reihenfolge (für schnelle Ausführung):

1. **Tab 1: Diagonal #1**
 - Seed: `aqiosqqmacybpqxqsjniuaylmxxiwqoxqmeqyxbbtbonsjjrcwpxxdd`
i - Identity: `OBWIIPWFPOWIQCHGJHKFZNMSSYOBYNNDLUEXAELXKEROIUKIXEUXMLZBICUD`

2. **Tab 2: Diagonal #2**
 - Seed: `gwuxommmmfmtbwfzsngmukwbiltxqdknmmmnypeftamronjmablhtrr`
 - Identity: `OQOOMLAQLGOJFFAYGXALSTDVDGQDWKWGDQJRMNZSODHMWWWNSLSQZZAHOAZE`

3. **Tab 3: Diagonal #3**
 - Seed: `acgjgqqyilbpxdrborfgwfzbbbnlqnghddelvlxxxlbnnnfbllpbnnn`
 - Identity: `WEZPWOMKYYQYGDZJDUEPIOTTUKCCQVBYEMYHQUTWGAMHFVJJVRCQLMVGYDGG`

4. **Tab 4: Diagonal #4**
 - Seed: `giuvfgawcbbffkvbmfjeslhbbfbfwzwnnxcbqbbjrvfbnvjltjbbbht`
 - Identity: `BUICAHKIBLQWQAIONARLYROQGMRAYEAOECSZCPMTEHUIFXLKGTMAPJFDCHQI`

5. **Tab 5: Vortex #1**
 - Seed: `uufeemuubiyxyxduxzcfbihabaysacqswsgabobknxbzciclyokobml`
 - Identity: `FAEEIVWNINMPFAAWUUYMCJXMSFCAGDJNFDRCEHBFPGFCCEKUWTMCBHXBNSVL`

6. **Tab 6: Vortex #2**
 - Seed: `hjbrfbhtbzjlvrbxtdrforbwnacahaqmsbunbonhtrhnjkxkknkhwcb`
 - Identity: `PRUATXFVEFFWAEHUADBSBKOFEQTCYOXPSJHWPUSUKCHBXGMRQQEWITAELCNI`

7. **Tab 7: Vortex #3**
 - Seed: `jklmnoipdqorwsictwwuiyvmofiqcqsykmkacmokqyccmcogocqcscw`
 - Identity: `RIOIMZKDJPHCFFGVYMWSFOKVBNXAYCKUXOLHLHHCPCQDULIITMFGZQUFIMKN`

8. **Tab 8: Vortex #4**
 - Seed: `xyzqaubquuqbqbyqayeiyaqymmemqqqmmqsqeqazsmogwoxkirmjxmc`
 - Identity: `DZGTELPKNEITGBRUPCWRNZGLTMBCRPLRPERUFBZHDFDTFYTJXOUDYLSBKRRB`

## Ausführungs-Strategie

### Option A: Schnell (wenn du schnell bist)
1. **Phase 1 - Vorbereitung (2-3 Minuten):**
 - Öffne alle 8 Tabs
 - Logge dich in jedem Tab mit dem entsprechenden Seed ein
 - Navigiere zu GENESIS Asset in jedem Tab
 - Bereite den Kauf vor (Menge eingeben, aber NICHT bestätigen)

2. **Phase 2 - Kauf (30 Sekunden):**
 - Gehe schnell durch alle 8 Tabs
 - Bestätige den Kauf in jedem Tab nacheinander
 - So schnell wie möglich, aber nicht panisch

### Option B: Sicher (wenn du unsicher bist)
1. **Ein Tab nach dem anderen:**
 - Tab 1: Login → GENESIS finden → Kaufen → Bestätigen
 - Tab 2: Login → GENESIS finden → Kaufen → Bestätigen
 - ... usw.
 - Dauert länger (5-10 Minuten), aber sicherer

## Wichtige Hinweise

- **Timing ist NICHT kritisch:** 2-3 Minuten Unterschied zwischen den Käufen ist OK
- **Contract ID:** `POCCZYCKTRQGHFIPWGSBLJTEQFDDVVBMNUHNCKMRACBGQOPBLURNRCBAFOBD`
- **Asset Name:** GENESIS
- **Nach dem Kauf:** Warte 1-2 Minuten, dann prüfe mit dem Monitoring-Script

## Nach dem Kauf

Führe aus:
```bash
cd ${PROJECT_ROOT}
source venv-tx/bin/activate
python3 scripts/verify/asset_monitor.py
```

Oder manuell prüfen:
```bash
python3 scripts/verify/contract_analysis.py
```

## Troubleshooting

- **"Seed nicht gefunden":** Prüfe, ob der Seed korrekt kopiert wurde (55 Zeichen, nur Kleinbuchstaben)
- **"Asset nicht gefunden":** Suche nach "GENESIS" oder Contract ID
- **"Balance zu niedrig":** Prüfe, ob die Layer-2 Identitäten genug QU haben
