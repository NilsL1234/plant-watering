# Notitzen

## Testen des MCP (10-bit-Analog-Digital-Umwandler, Spannung->Bitwert)

#### Datei: mcp_test.py
#### Ziel: Sicherstellen, dass Pi und MCP über SPI (Serial Perifial Interface) kommunizieren können


### Aufbau:

Verbindungen: 
- MOSI (Master-Out-Slave-In): Daten von Pi zu MCP
- MISO (Master-In-Slave-Out): Daten von MCP zu Pi
- SCLK (Serial Clock): Taktgeber
- CS (Chip Select): Geräteauswahl
- CHO des MCP wird testweise an GND und 3,3V gelegt

Das Programm öffnet die Verbindung spi.open(0,0), die erste 0 legt den Bus fest, die Zweite das Gerät, also den MCP.
Der Takt wird auf maximal 1MHz festgelegt.
Mit response = spi.xfer2([1, 128, 0]) sendet der Pi 3 bytes an den MCP. Die 1 startet die Anfrage, die 128 sagt, Single-ended-Modus (miss CH0 relativ zu GND) und verwende den Kanal CH0 des MCPs. Die 0 am Ende ist der Dummy, damit der Pi weiter Takte für die Response des MCP erzeugt.
 


### Erwartung:
Nahe 0 bei GND und 1023 bei 3,3V (da 10 bit antwort -> 1023 ist max)

### Ergebnis:
Messungen erfolgreich. Kommunikation zwischen Pi und MCP über SPI funktioniert für den Minimal- und Maximalwert

### Erkenntnis:

- Funktionsweise und Aufbau von SPI. Man braucht einen Takt und muss sagen, welches Gerät angesprochen wird. Es können mehrere Geräte den selben Bus verwenden. Der Pi gibt einen Takt vor, der dieser Regelt den ablauf der Datenübertragung. 1 takt gleich 1 bit. 



## Testen des Sensors: 

### Ziel:

Herausfinden, welche Werte der Feuchtigkeitssensor bei verschiedener Umgebung annimmt und wie stabil die Messwerte sind.
Wichtig ist dabei, welche Werte bei trockener/feuchter Erde entstehen, um ein erstes Bild zu bekommen, wann später automatisch gewässert werden sollte. 

### Aufbau: 

Es werden verschiedene Umgebungen mehrfach (5x) getestet:
- trockene Erde
- leicht feuchte Erde (1x Sprühen)
- feuchte Erde (1x gießen)
- nasse Erde (3 x gießen)
- Wasser
- warmes Wasser
- warmes Salzwasser



### Erwartung:

Der Sensor basiert auf der Leitfähigkeit von Strom.
Umso höher die Leitfähigkeit, desto höher der Messwert.
Wasser leitet Strom besser, somit sollte der Wert mit steigender Feuchtigkeit auch steigen. 
Salz verstärkt noch die Leitfähigkeit und dient als Vergleich.

### Ergebnis:

| Messumgebung | Messwert 1 | Messwert 2 | Messwert 3 | Messwert 4 | Messwert 5 | Durchschnitt |
|---|---|---|---|---|---|---|
| Luft | 1000 | 1000 | 1001 | 998 | 996 | 999.0 |
| trockene Erde | 998 | 1002 | 1007 | 1023 | 1007 | 1006.4 |
| leicht feuchte Erde | 958 | 955 | 959 | 956 | 951 | 955.8 |
| feuchte Erde (1x gießen)| 614 | 616 | 612 | 610 | 613 | 613.0|
| nasse Erde (3 x gießen) | 433 | 438 | 447 | 453 | 457 | 445.6 | 
| Wasser | 420 | 434 | 439 | 449 | 455 | 439.4 |
| Warmes Wasser | 220 | 245 | 256 | 269 |  282 | 254.4 |
| Warmes Salzwasser | 182 | 179 | 185 | 198 | 194 | 187.6 |

### Erkenntnis: 

- Umso besser die Leitfähigkeit, umso niedriger der Messwert
- Trockene Erde hat ca. einen Wert von 1000
- leicht feucht (1x Sprühen) ist leicht spürbar (ca. -50)
- nasse Erde und reines Wasser sind fast identisch (450)
- Grenze der Bewässerung muss über der von nasser Erde (3x gießen) liegen, da es nicht unterscheidbar von stehendem Wasser ist!
- Erster Zielwert beim gießen könnte zwischen 500 und 600 liegen

## Testen der Pumpe

### Ziel: 

Wie viel Wasser liefert die Pumpe?

### Aufbau: 

Pumpe 60 Sekunden laufen lassen, Menge messen. 

### Erwartung: 

X

### Ergebnis: 

Die Pumpe pumpt ca 25 ml pro Minute

### Erkenntnis: 

Wie lange die Pumpe laufen muss, um Menge x an Wasser zu befördern.


### Ziel:

Kalibrierung folgender Werte: 

- Beginn Pumpen
- Ende Pumpen
- Pumpintervalle

### Aufbau: 

- Trockene Erde wird bei einem Wert von 1000 erreicht (Beginn Pumpen)
- Ende Pumpen idealerweise bei ca. 500

- Frage: 
    - Wie viel Wasser ist nötig, um einen wert von 500 zu erreichen
    - Wie lange muss die Pumpe ca laufen, um diesen Wert zu erreichen
    - 




### Erwartung: 
### Ergebnis: 
### Erkenntnis: 











### Ziel:
### Aufbau: 
### Erwartung: 
### Ergebnis: 
### Erkenntnis: 







