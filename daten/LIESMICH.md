# Daten für die App „Wetter AW“

## ski_areas.tsv.gz

Skigebiete weltweit für die Karte „Berg- und Skiwetter“: Name, Breite, Länge,
tiefster und höchster Punkt (m), Pistenkilometer leicht/mittel/schwer, Zahl
der Lifte, Website — eine Zeile je Skigebiet, durch Tabulatoren getrennt,
gzip-gepackt.

- **Quelle:** [OpenSkiMap](https://openskimap.org/), berechnet aus
  [OpenStreetMap](https://www.openstreetmap.org/).
- **Lizenz:** [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/) —
  © OpenStreetMap-Mitwirkende. Diese Datei ist eine abgeleitete Datenbank
  und steht ebenfalls unter der ODbL.
- **Aktualisierung:** jeden Montag automatisch durch die GitHub-Aktion
  „Skigebiete aktualisieren“ (`.github/workflows/skigebiete.yml`, Skript
  `tools/make_ski_areas.py`). Nur Skigebiete in Betrieb (nicht stillgelegt)
  mit mindestens 1 km Abfahrten oder 2 Liften.
- Die App holt die Datei höchstens einmal im Monat und nur, wenn sie sich
  geändert hat; ohne Netz nimmt sie ihre eingebaute Liste.
