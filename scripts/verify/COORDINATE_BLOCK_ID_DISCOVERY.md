# Koordinaten-basierte Block-ID Entdeckung

## Kritische Erkenntnis

**Für Diagonal Identities (#1-4):**
- **Identity #1**: Start-Koordinate (0, 0) → `r // 32 = 0` 
- **Identity #2**: Start-Koordinate (32, 0) → `r // 32 = 1` 
- **Identity #3**: Start-Koordinate (64, 0) → `r // 32 = 2` 
- **Identity #4**: Start-Koordinate (96, 0) → `r // 32 = 3` 

**Formel:** `Block-ID = r // 32` für Diagonal Identities

## Bedeutung

Die **Block-ID** ist direkt in der **Start-Koordinate** kodiert:
- Die **Row-Koordinate** geteilt durch 32 ergibt die Block-ID (0-3 für Diagonal)
- Dies entspricht `Identity-Index - 1`

## Für Vortex Identities (#5-8)

Die Vortex Identities haben eine andere Koordinaten-Struktur:
- Sie verwenden Ring-Positionen um das Zentrum (64, 64)
- Die Block-ID könnte in der **Radius** oder **Winkel-Position** kodiert sein

## Nächste Schritte

1. **Bestätige die Block-ID-Formel** für alle 8 Identities
2. **Analysiere Vortex-Koordinaten** um die Block-ID-Formel zu finden
3. **Teste die Block-IDs** als Payload für den Smart Contract

## Smart Contract Payload

Wenn diese Block-IDs korrekt sind, sollten wir an den Smart Contract senden:
- **Diagonal #1**: Block-ID 0 (oder 1, je nach 0-based/1-based)
- **Diagonal #2**: Block-ID 1 (oder 2)
- **Diagonal #3**: Block-ID 2 (oder 3)
- **Diagonal #4**: Block-ID 3 (oder 4)
- **Vortex #1-4**: Block-IDs 4-7 (oder 5-8) - noch zu bestimmen
