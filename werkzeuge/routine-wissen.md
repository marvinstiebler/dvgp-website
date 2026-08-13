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

Der Auftragstext steht in der Routine selbst. Er wird über die RemoteTrigger-API
gepflegt, nicht aus dieser Datei gelesen — diese Datei dokumentiert nur.

## Was die Routine kann und was nicht

**Sie schreibt zuverlässig.** Der Lauf vom 13.08.2026 hat einen vollständigen,
regelkonformen Beitrag erzeugt, gebaut, den Themenplan gepflegt und committet.

**Sie kann nicht pushen.** Und selbst wenn sie es könnte, würde der Push nichts
veröffentlichen. Zwei getrennte Ursachen, beide am 13.08.2026 nachgewiesen.

### Ursache 1 — die Sitzung hat kein Schreib-Token

Nachgewiesen im Diagnoselauf `cse_01BKLeXQd5o1LmqTo4xWPxgq`:

| Prüfung | Ergebnis |
|---|---|
| `GITHUB_TOKEN` im Container | Platzhalter `proxy-injected`, kein echtes Token |
| Anmeldung | wird von einem Git-Proxy zur Laufzeit eingespritzt |
| `api.github.com` durch den Proxy | **403, auch ohne Auth-Header** — der Kanal ist gesperrt |
| `git clone` | funktioniert |
| `git push` auf einen Testzweig | `403` |
| `add_repo` mit `access: "push"` **vor** jedem Lesezugriff | ändert nichts |
| `list_repos` | meldet `visibility: public, can_push: true` |

`can_push: true` bezieht sich auf Marvins GitHub-Konto, nicht auf das Token, das
der Proxy einspritzt. Der Proxy hat für dieses Repo nur Leserechte.

Die 403-Meldungen der GitHub-API (`Resource not accessible by integration`) sind
eine Sackgasse und **kein** Hinweis auf fehlende App-Rechte — dieser Kanal ist
für alle Sitzungen gesperrt, mit und ohne Token. Nicht noch einmal untersuchen.

**Die Lösung** steht in der Anthropic-Doku unter *GitHub authentication options*:
Cloud-Sitzungen bekommen Repo-Zugriff auf genau zwei Wegen — über die Claude-
GitHub-App oder über `/web-setup`, das den lokalen `gh`-Token mit dem Claude-Konto
abgleicht. Marvins lokaler `gh` hat die Scopes `gist, read:org, repo`; `repo`
schließt Schreibrechte ein.

```
claude          # im Terminal
/web-setup
```

Danach hat jede neue Cloud-Sitzung dieselben Rechte wie der lokale `gh`.
Der frühere Hinweis auf `github.com/settings/installations` war falsch — die
App-Installation steuert laut Doku ausdrücklich **nicht** den Sitzungszugriff,
sondern nur die PR-Webhooks für Auto-fix.

### Ursache 2 — Workers Builds ist nicht verbunden

Ein Push auf `main` hat diese Seite **noch nie** deployt. `wrangler deployments
list` zeigt ausschließlich manuelle Deployments von Marvins Rechner; das letzte
vor dem 13.08. stammt vom 12.08. um 05:10 und lag damit *vor* dem letzten Push.

Solange das so ist, gilt: nach jedem Push muss einmal

```bash
npx wrangler deploy
```

von diesem Rechner laufen. Wer das dauerhaft loswerden will, verbindet das Repo
im Cloudflare-Dashboard unter *Workers & Pages → dvgp-website → Settings → Build*
mit GitHub. Erst dann stimmt der Satz „der Push löst das Deployment aus".

## Was jetzt eingebaut ist

Damit nie wieder Arbeit verlorengeht, sendet die Routine **immer** — auch bei
erfolgreichem Push — den fertigen Beitrag und einen `git format-patch` per
SendUserFile. Anwenden lässt sich der Patch mit:

```bash
git am beitrag.patch
```

Außerdem prüft sie am Ende die Live-URL und schreibt in den Bericht, ob der
Beitrag im Repo liegt, veröffentlicht ist, oder beides nicht.

Der Bericht kommt immer als Tabelle mit Schritt, Ergebnis und exakter
Fehlermeldung. Sie soll nichts beschönigen und keine neue Sitzung vorschlagen.

## Erledigt

Der Wegwerf-Trigger `trig_01XcD9c2ST8Xe7yVVVMVxMCg` („TEMP Push-Diagnose") hat die
Befunde oben erzeugt und ist deaktiviert. Er kann gelöscht werden.
