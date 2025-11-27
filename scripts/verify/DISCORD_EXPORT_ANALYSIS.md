# Discord CFB Export - Analyse & Lösungsansätze

## Aktueller Ansatz

### Wie funktioniert es jetzt?

1. **DiscordChatExporter.Cli** wird verwendet
2. **Prozess:**
 ```
 DiscordChatExporter.Cli export 
 --channel 768890598736003092
 --token <TOKEN>
 --output <FILE>
 --format Json
 ```

3. **Problem:** Exportiert ALLE Nachrichten im Channel (kann Stunden dauern bei großen Channels)

4. **Filterung:** Nach dem Export werden CFB-Nachrichten gefiltert (User ID: 395234579805503489)

### Warum ist es langsam?

- **DiscordChatExporter** muss ALLE Nachrichten durchgehen
- Bei großen Channels (z.B. 10.000+ Nachrichten) dauert das sehr lange
- Rate Limits von Discord API
- JSON-Parsing großer Dateien (15MB+)

## Alternative Ansätze

### Option 1: Filter während Export (NICHT FUNKTIONIERT)

```bash
--filter "from:395234579805503489"
```

**Problem:** DiscordChatExporter filtert auf Client-Seite, muss trotzdem alle Nachrichten laden.

### Option 2: Batch-Export mit --after Parameter

```python
# Batch 1: Neueste 100 Nachrichten
export --after <MESSAGE_ID>

# Batch 2: Nächste 100 (älter)
export --after <LAST_MESSAGE_ID>
```

**Vorteil:** 
- Kleine Batches (100 Nachrichten)
- Sofortiges Filtern nach jedem Batch
- Kann abgebrochen werden

**Nachteil:**
- Muss trotzdem durch alle Nachrichten gehen
- Viele API-Calls

### Option 3: Discord API direkt (OHNE DiscordChatExporter)

**Vorteil:**
- Direkte Kontrolle
- Kann genau 100 Nachrichten pro Request holen
- Kann sofort filtern

**Nachteil:**
- Mehr Code nötig
- Rate Limit Handling selbst implementieren

### Option 4: Reverse-Chronological Export (NEUESTE ZUERST)

```python
# Starte mit neuesten Nachrichten
# Gehe rückwärts durch die Zeit
# Stoppe wenn keine CFB-Nachrichten mehr kommen
```

**Vorteil:**
- Findet CFB-Nachrichten schneller (wenn er aktiv war)
- Kann früher stoppen

## Empfohlene Lösung: Hybrid-Ansatz

### Schritt 1: Schneller Scan (neueste Nachrichten zuerst)

```python
# Exportiere neueste 1000 Nachrichten
# Filtere CFB
# Wenn CFB gefunden → weiter
# Wenn keine CFB → stoppe oder gehe weiter zurück
```

### Schritt 2: Batch-Processing mit --after

```python
# Verwende --after um rückwärts zu gehen
# 100 Nachrichten pro Batch
# Sofort filtern und speichern
# Stoppe nach 5 leeren Batches
```

### Schritt 3: Intelligente Pause

```python
# Wenn Rate Limit → warte
# Wenn zu langsam → reduziere Batch-Größe
# Wenn CFB-Dichte niedrig → größere Sprünge
```

## DiscordChatExporter Dokumentation

### Wichtige Parameter

- `--channel <ID>` - Channel ID
- `--token <TOKEN>` - Discord Token
- `--format Json` - JSON Format
- `--after <MESSAGE_ID>` - Nur Nachrichten nach dieser ID
- `--before <MESSAGE_ID>` - Nur Nachrichten vor dieser ID
- `--partition <N>` - Teilt Export in N-Nachrichten-Blöcke
- `--filter <EXPR>` - Filter Expression (z.B. "from:USER_ID")

### Filter Syntax

```
from:USER_ID - Nur von diesem User
has:link - Mit Links
has:embed - Mit Embeds
pins:true - Gepinnte Nachrichten
```

**Problem:** Filter wird NACH dem Laden angewendet, nicht während des API-Calls!

## Discord API Limits

- **Rate Limit:** ~50 Requests/Sekunde
- **Message Limit:** 100 Nachrichten pro Request
- **Timeout:** Requests können 30+ Sekunden dauern

## Empfohlene Implementierung

### Schneller Ansatz (für CFB-spezifisch)

1. **Starte mit neuesten Nachrichten**
2. **100 Nachrichten pro Batch**
3. **Sofort filtern (nur CFB)**
4. **Speichern**
5. **Gehe rückwärts mit --after**
6. **Stoppe nach 10 leeren Batches**

### Code-Struktur

```python
def export_cfb_fast():
 all_cfb = []
 last_message_id = None
 batch_size = 100
 empty_batches = 0
 
 while empty_batches < 10:
 # Export batch
 batch = export_batch(after=last_message_id, limit=batch_size)
 
 # Filter CFB
 cfb = [m for m in batch if m.author.id == CFB_USER_ID]
 
 if cfb:
 all_cfb.extend(cfb)
 last_message_id = cfb[-1].id
 empty_batches = 0
 else:
 empty_batches += 1
 
 # Save immediately
 save(all_cfb)
 
 # Small delay
 time.sleep(0.5)
```

## Performance-Vergleich

| Methode | Geschwindigkeit | Effizienz |
|---------|----------------|-----------|
| Vollständiger Export | ⏱⏱⏱⏱⏱ (sehr langsam) | |
| Batch mit Filter | ⏱⏱⏱ (langsam) | |
| Reverse-Chronological | ⏱⏱ (schneller) | |
| Discord API direkt | ⏱ (am schnellsten) | |

## Nächste Schritte

1. Implementiere Reverse-Chronological Export
2. Verwende --after für rückwärts-Navigation
3. Stoppe früh wenn keine CFB mehr
4. Speichere sofort nach jedem Batch
5. Implementiere Rate Limit Handling
