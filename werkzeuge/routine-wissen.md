# Routine: Wissens-Beitrag Mo/Do

| | |
|---|---|
| Name | DVGP Wissen — Beitrag (Mo/Do) |
| ID | `trig_01GkwJbEa8epTvbwo57GqZ2e` |
| Takt | `0 6 * * 1,4` — Montag und Donnerstag 06:00 UTC = **08:00 Berlin** |
| Modell | `claude-opus-5` |
| Umgebung | Default (`env_011fpeEsxWpkqwY6cMbqGp2Y`) |
| Repo | wird zur Laufzeit per `add_repo` geholt, **nicht** als Quelle eingehängt |
| Werkzeuge | Bash, Read, Write, Edit, Glob, Grep, ToolSearch, SendUserFile |
| Verwalten | https://claude.ai/code/routines |

Der Auftragstext steht in der Routine selbst und wird über die RemoteTrigger-API
gepflegt. Diese Datei dokumentiert nur.

## Stand: 14.08.2026 — Push ja, Deployment noch nicht

| | |
|---|---|
| Push aus der Cloud-Sitzung | **funktioniert**, nachgewiesen im Lauf `cse_01JuzPTuCJDwwGgEreu1YBkD` (Push auf einen Testzweig kam auf GitHub an) |
| Deployment durch den Push | **noch nicht bestätigt** — Testpush `3abb84d` löste in elf Minuten keinen Build aus |

Solange das zweite offen ist, landet der Beitrag der Routine im Repo, geht aber erst
mit einem `npx wrangler deploy` von Marvins Rechner online. Details und was zu prüfen
ist: [DEPLOYMENT.md](../DEPLOYMENT.md).

## Was zwei Tage lang kaputt war — und warum

Zwei getrennte Fehler, die sich gegenseitig verdeckt haben. Der zweite fiel erst auf,
als der erste behoben war.

### Fehler 1 — die Cloud-Sitzung hatte kein Schreib-Token

Der Diagnoselauf `cse_01BKLeXQd5o1LmqTo4xWPxgq` vom 13.08. hat es auseinandergenommen:

| Prüfung | Ergebnis |
|---|---|
| `GITHUB_TOKEN` im Container | Platzhalter `proxy-injected`, kein echtes Token |
| Anmeldung | wird von einem Git-Proxy zur Laufzeit eingespritzt |
| `api.github.com` durch den Proxy | **403, auch ohne Auth-Header** — der Kanal ist gesperrt |
| `git clone` | funktioniert |
| `git push` | `403` |
| `add_repo` mit `access: "push"` vor jedem Lesezugriff | ändert nichts |
| `list_repos` | meldet `can_push: true` |

`can_push: true` bezieht sich auf Marvins GitHub-Konto, nicht auf das Token, das der
Proxy einspritzt. Der Proxy hatte für dieses Repo nur Leserechte.

**Behoben durch** `/web-setup` in einer interaktiven Terminal-Sitzung. Der Befehl hängt
den lokalen `gh`-Token (Scopes `gist, read:org, repo`) ans Claude-Konto. Laut Anthropic-
Doku ist das einer von genau zwei Wegen; der andere ist die Claude-GitHub-App.

Zwei Sackgassen, die nicht noch einmal untersucht werden müssen:

- Die 403 der GitHub-API (`Resource not accessible by integration`) sind **kein** Hinweis
  auf fehlende App-Rechte. Der Kanal ist für alle Sitzungen gesperrt, mit und ohne Token.
- `github.com/settings/installations` ist die falsche Stelle. Die App-Installation steuert
  laut Doku ausdrücklich nicht den Sitzungszugriff, sondern nur die PR-Webhooks für
  Auto-fix.

### Fehler 2 — Workers Builds war nie verbunden

Ein Push auf `main` hat die Seite **nie** deployt. `wrangler deployments list` zeigte bis
zum 13.08. ausschließlich manuelle Deployments; das letzte davor lag am 12.08. um 05:10
und damit *vor* dem letzten Push.

**Am 14.08. angegangen** über *Workers & Pages → dvgp-website → Einstellungen → Erstellen
→ Git-Repository verbinden*, aber noch nicht nachweislich wirksam — siehe oben und
[DEPLOYMENT.md](../DEPLOYMENT.md).

Achtung beim Verbinden: Cloudflare schlägt ein vorhandenes API-Token aus einem anderen
Projekt vor und meldet dazu selbst fehlende Rechte. Das ist der wahrscheinlichste Grund,
wenn ein Build nicht startet oder abbricht. Hier gehört ein eigenes Token hin, Vorlage
*Cloudflare Workers bearbeiten*, Zonenressource `dvgp.info`.

## Das Sicherheitsnetz bleibt

Auch jetzt, wo der Push funktioniert, sendet die Routine bei **jedem** Lauf den fertigen
Beitrag und einen `git format-patch` per SendUserFile. Das kostet nichts und heißt: selbst
wenn Push oder Build einmal ausfallen, ist die Arbeit da. Anwenden mit:

```bash
git am beitrag.patch
```

Am Ende prüft sie die Live-URL und schreibt in den Bericht, ob der Beitrag im Repo liegt
und ob er veröffentlicht ist. Der Bericht kommt als Tabelle mit Schritt, Ergebnis und
exakter Fehlermeldung. Nichts beschönigen, keine neue Sitzung vorschlagen.

## Aufräumen

Der Wegwerf-Trigger `trig_01XcD9c2ST8Xe7yVVVMVxMCg` („TEMP Push-Diagnose") hat die
Befunde oben erzeugt, ist deaktiviert und kann gelöscht werden.
