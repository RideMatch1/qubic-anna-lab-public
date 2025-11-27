# Discord CFB Export - Übersicht & Dokumentation

## Problemstellung

**Ziel:** Alle Nachrichten von CFB (User ID: 395234579805503489) aus dem Aigarth-Channel (768890598736003092) exportieren.

**Herausforderung:** 
- Channel hat viele Nachrichten (10.000+)
- Vollständiger Export dauert sehr lange (30+ Minuten)
- Wir wollen NUR CFB-Nachrichten, nicht alle

## Aktuelle Methoden

### Methode 1: Vollständiger Export + Filter
```bash
DiscordChatExporter.Cli export --channel <ID> --token <TOKEN> --format Json
# Dann: Filtere CFB-Nachrichten aus JSON
```
**Problem:** Exportiert ALLE Nachrichten, sehr langsam

### Methode 2: Batch-Export mit --after
```bash
# Batch 1: Neueste Nachrichten
export --after <MESSAGE_ID>

# Batch 2: Ältere Nachrichten 
export --after <LAST_MESSAGE_ID>
```
**Vorteil:** Kleine Batches, kann abgebrochen werden
**Nachteil:** Muss trotzdem durch alle Nachrichten

### Methode 3: Filter während Export
```bash
export --filter "from:395234579805503489"
```
**Problem:** Filter wird NACH dem Laden angewendet, nicht während API-Call

## Empfohlene Lösung: Reverse-Chronological

### Konzept

1. **Starte mit neuesten Nachrichten**
2. **Exportiere 100 Nachrichten pro Batch**
3. **Filtere sofort CFB-Nachrichten**
4. **Speichere sofort**
5. **Gehe rückwärts mit --after Parameter**
6. **Stoppe nach 10 leeren Batches**

### Vorteile

- Findet CFB-Nachrichten schneller (wenn er aktiv war)
- Kann früher stoppen
- Sofortiges Speichern (kein Datenverlust)
- Kleine Batches (schneller)

### Code-Flow

```
1. Export Batch (neueste 100 Nachrichten)
 ↓
2. Filtere CFB-Nachrichten
 ↓
3. Speichere sofort
 ↓
4. Nimm letzte Message-ID als --after für nächsten Batch
 ↓
5. Wiederhole (gehe rückwärts in der Zeit)
 ↓
6. Stoppe wenn 10 Batches ohne CFB
```

## DiscordChatExporter Parameter

### Wichtige Optionen

| Parameter | Beschreibung | Beispiel |
|-----------|-------------|----------|
| `--channel` | Channel ID | `768890598736003092` |
| `--token` | Discord Token | `MzAzMDcz...` |
| `--format` | Export Format | `Json`, `HtmlDark`, `PlainText` |
| `--after` | Nur Nachrichten nach dieser ID | `1234567890123456789` |
| `--before` | Nur Nachrichten vor dieser ID | `1234567890123456789` |
| `--filter` | Filter Expression | `from:USER_ID` |
| `--partition` | Teilt in Blöcke | `100` |

### Filter Syntax

```
from:USER_ID # Nur von diesem User
has:link # Mit Links
has:embed # Mit Embeds
pins:true # Gepinnte Nachrichten
```

**WICHTIG:** Filter wird Client-seitig angewendet, nicht während API-Call!

## Discord API Limits

- **Rate Limit:** ~50 Requests/Sekunde
- **Message Limit:** 100 Nachrichten pro Request (max)
- **Timeout:** Requests können 30+ Sekunden dauern bei großen Channels

## Performance-Optimierung

### Tipps

1. **Kleine Batches:** 100 Nachrichten pro Batch
2. **Sofortiges Filtern:** Filtere direkt nach Export
3. **Sofortiges Speichern:** Kein Datenverlust bei Abbruch
4. **Intelligente Pause:** 0.3-0.5 Sekunden zwischen Batches
5. **Frühes Stoppen:** Stoppe nach X leeren Batches

### Geschwindigkeit

- **Vollständiger Export:** ~30-60 Minuten (bei 10.000+ Nachrichten)
- **Reverse-Chronological:** ~5-15 Minuten (abhängig von CFB-Aktivität)
- **Direkte Discord API:** ~2-5 Minuten (mehr Code nötig)

## Dateien

### Export-Scripts

- `export_cfb_reverse_chronological.py` - **EMPFOHLEN** (schnell, intelligent)
- `export_cfb_fast_batch.py` - Batch-Export
- `export_cfb_only.py` - Filter-Export (langsam)
- `export_cfb_incremental.py` - Incremental (langsam)

### Output

- `outputs/derived/cfb_discord_messages/cfb_messages_channel_768890598736003092.json`
 - Enthält alle CFB-Nachrichten
 - Format: JSON Array
 - Wird sofort gespeichert nach jedem Batch

## Verwendung

```bash
export DISCORD_TOKEN='your_token_here'
python3 scripts/verify/export_cfb_reverse_chronological.py
```

## Troubleshooting

### Problem: Export hängt
**Lösung:** Timeout erhöhen oder Batch-Größe reduzieren

### Problem: Rate Limits
**Lösung:** Pause zwischen Batches erhöhen (0.5s → 1s)

### Problem: Zu langsam
**Lösung:** Verwende `export_cfb_reverse_chronological.py` statt vollständigem Export

### Problem: Keine CFB-Nachrichten
**Lösung:** Prüfe User ID, prüfe Channel ID, prüfe ob CFB in diesem Channel aktiv war
