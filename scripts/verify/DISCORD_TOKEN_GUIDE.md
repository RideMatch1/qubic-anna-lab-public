# Discord Token Guide

## Wie man den Discord Token bekommt

### Methode 1: Browser Developer Tools (Empfohlen)

1. Öffne Discord im Browser (https://discord.com)
2. Logge dich ein
3. Drücke `F12` oder `Cmd+Option+I` (Mac) um Developer Tools zu öffnen
4. Gehe zum **Network** Tab
5. Drücke `F5` oder `Cmd+R` um die Seite neu zu laden
6. Suche nach einer Request die mit "messages" oder "api" beginnt
7. Klicke auf die Request
8. Gehe zum **Headers** Tab
9. Scrolle zu **Request Headers**
10. Kopiere den Wert von `authorization` (beginnt mit `MTA...` oder `OD...`)

### Methode 2: Token speichern

Erstelle eine Datei `~/.discord_token`:
```bash
echo "DEIN_TOKEN_HIER" > ~/.discord_token
chmod 600 ~/.discord_token
```

Oder als Environment Variable:
```bash
export DISCORD_TOKEN='DEIN_TOKEN_HIER'
```

## Script ausführen

```bash
# Mit Environment Variable
export DISCORD_TOKEN='dein_token'
python3 scripts/verify/export_cfb_discord_fast.py

# Oder mit Token-Datei
echo "dein_token" > ~/.discord_token
python3 scripts/verify/export_cfb_discord_fast.py
```

## Channel Info

- **Channel URL**: https://discord.com/channels/768887649540243497/768890598736003092
- **Guild ID**: 768887649540243497
- **Channel ID**: 768890598736003092
- **CFB User ID**: 395234579805503489
