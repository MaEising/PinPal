### TODO

- Alles auf Englisch übersetzen, code nur in Englisch
- flaticon.com für bilder und icons nennen
- im usermanagement und in gamecreation site Usernamen umbrechen ab 7 Zeichen, mehr als 10 Zeichen sollten mit ... versteckt werden
- Usability bei der Menüführung: wie vermitteln dass man sich durch den Button ins Menü klickt? Flow ändern das man erst auf registrieren Seite landet und dann vlcht ein Button mit "direkt zum login"

### Work in Progress:

- Logging in jeder funktion unterbringen (info) warning / debug im laufe des codes und an stellen wo prints gesetzt sind
- Usability verbessern und am Handy Strichliste nutzbar machen
  - game_configuration: wip: Funktion um hideRows sichtbar zu machen
    - die Rows müssen beim erneuten Aufruf der Funktion wieder versteckt werden -> bleiben permanent Sichtbar nach dem ersten klicken

### IDEAS

- Option beim anlegen von Strafen die das invertieren erlaubt. Betrag wird nicht dem Spieler angerechnet sondern allen anderen (z.B. beim werfen von neunen)
- kleines Fragezeichen oder so neben den Button den man als Erklärung dann anklicken kann

### bugs and errors

- create_or_load game player.username table looks super shit if more than 12 players are defined
