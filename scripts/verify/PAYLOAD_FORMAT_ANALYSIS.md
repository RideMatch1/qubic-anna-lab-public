# Payload-Format Analyse

## Problem

Unsere Transaktionen mit Block-ID-Payload (1-8) sind **NICHT beim Contract angekommen**.

## Mögliche Ursachen

### 1. Payload-Format falsch
- Aktuell: Block-ID als **String** (`"1"`, `"2"`, etc.)
- Mögliche Alternativen:
 - **Integer** (1 Byte: `0x01`, `0x02`, etc.)
 - **Base-26 encoded** (aus Matrix-Werten)
 - **Koordinaten** (r, c als Bytes)
 - **Kombination** mehrerer Werte

### 2. Transaktions-Signatur falsch
- Payload wird VOR Signatur eingefügt → Signatur sollte korrekt sein
- Aber: Vielleicht ist die Transaktions-Struktur falsch?

### 3. Timing-Problem
- Alle Transaktionen im gleichen Tick → Vielleicht zu schnell?
- Contract erwartet bestimmte Reihenfolge?

### 4. Block-ID falsch
- Vielleicht ist es nicht `r // 32 + 1`, sondern:
 - `r // 32` (0-basiert)
 - Eine andere Formel
 - Nicht die Row-Koordinate, sondern Column oder Kombination

## Test-Strategie

1. **Prüfe Transaktions-Broadcast** - Wurden sie überhaupt gesendet?
2. **Teste verschiedene Payload-Formate**:
 - String: `"1"`, `"2"`, etc.
 - Integer (1 Byte): `0x01`, `0x02`, etc.
 - Integer (4 Bytes): `0x00000001`, etc.
 - Base-26: Aus Matrix-Werten abgeleitet
3. **Prüfe Block-ID-Formel** - Ist `r // 32 + 1` wirklich korrekt?
4. **Teste ohne Payload** - Funktioniert die Transaktion überhaupt?
