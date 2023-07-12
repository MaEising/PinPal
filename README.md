### TODO

- Alles auf Englisch übersetzen, code nur in Englisch
- flaticon.com für bilder und icons nennen
- im usermanagement und in gamecreation site Usernamen umbrechen ab 7 Zeichen, mehr als 10 Zeichen sollten mit ... versteckt werden
- Usability bei der Menüführung: wie vermitteln dass man sich durch den Button ins Menü klickt? Flow ändern das man erst auf registrieren Seite landet und dann vlcht ein Button mit "direkt zum login"
- penalty Seite (und andere?) umdesignen: aussehen wie [hier](https://www.rockanutrition.de/pages/kalorienrechner-app#/step2). Ggf in Figma Linux zuerst anlegen
- error handling und validierung implementieren
- große funktionen kleiner machen

### Work in Progress:

- Logging in jeder funktion unterbringen (info) warning / debug im laufe des codes und an stellen wo prints gesetzt sind
- invert erzeugt eine Db PenaltyEntity die denn boolean Wert ob invertiert werden soll oder nicht enthält. Logik muss gebaut werden um beim Update Quantity call rauszufinden ob die Strafe invertiert ist. Falls dem so ist müssen die totalfine records mit dem payamount diese Strafe aller _anderen_ participants zu / ab gerechnet werden. Die Quantity wird dennoch beim Spieler der die "Strafe" geworfen hat eingetragen.
- Usability verbessern und media responsive design implementieren: auf der view game Seite werden die {{player_record.participant_name}}s neben dem Playeravatar angezeigt obwohl sie mit in den player square sollen. Fix implementieren

### IDEAS

- kleines Fragezeichen oder so neben den Button den man als Erklärung dann anklicken kann
- Tabelle unter Gamesummary die alle Strafen enthält braucht auch nen collapse button um die Strafen anzuzeigen, im default nur Namen und Geldbetrag

### bugs and errors
