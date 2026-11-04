


#1. Was prüfe ich?
#   Ich prüfe ob der MCP(Umwandler analog/digital-Signal) die spannung von dem ground (0V) an den PI schicken kann 
#   Der Pi schickt eine anfrage an den MCP und dieser antwortet. Involiert sind MOSI (anfrage pi an MCP), MISO(MCP sendet antwort), der Taktgeber und das singnal, das der MCP gerade angefragt wird, erst wenn das aktiv ist, beginnt der takt und die datenübertragung. 
#2. Was erwarte ich?
# wenn der mcp mit ground verbunden ist, sollte 0 oder etwas darüber ankommen
#3. Was würde ein anderes Ergebnis bedeuten?
# der mcp hat kein strom, im code ist was falsch, eines der kabel ist nicht richtig gesteckt, allgemein gesprochen
# Ziel:
# Ich prüfe, ob der Raspberry Pi über SPI den MCP3008 ansprechen kann.

# Testaufbau:
# CH0 ist mit GND verbunden.
# Deshalb liegt am analogen Eingang CH0 eine Spannung von 0 V an.

# Erwartung:
# Der MCP3008 sollte daraus einen digitalen Wert nahe 0 machen.

# Schritt 1:
# SPI-Bibliothek einbinden.

from spidev import SpiDev
import time

# Schritt 2:
# SPI-Objekt erzeugen.

spi = SpiDev()

# Schritt 3:
# SPI-Bus 0 und Gerät 0 öffnen.
# Das entspricht /dev/spidev0.0 und damit CE0.
spi.open(0,0)

# Schritt 4:
# SPI-Geschwindigkeit festlegen.
spi.max_speed_hz = 1_000_000
# Schritt 5:
# Anfrage an den MCP3008 senden:
# - Starte Messung
# - Nutze Single-ended-Modus
# - Lies Kanal CH0
# - Erzeuge genug Taktimpulse für die Antwort
response = spi.xfer2([1,128,0])

# Schritt 6:
# Rohantwort ausgeben.
print("Raw SPI response:",response)
# Schritt 7:
# Aus der Rohantwort den 10-Bit-ADC-Wert zusammensetzen.
value = ((response[1] & 3) << 8 | response[2])
# Schritt 8:
# ADC-Wert ausgeben.
print("SPI value:",value)

# Schritt 9:
# SPI-Verbindung schließen.
spi.close()

# Funktion für das Auslesen von CH0 des MCP. 

def read_chanel(spi, channel):
    request = [1, (8 + channel) << 4, 0]
    response = spi.xfer2(request)
    value = ((response[1] & 3)<< 8) | response[2] 
    return value;

channel_mcp = 0

for i in range(5):
    result = read_chanel(spi, channel_mcp)
    print(f"Das Ergebnis der Messung{i+1} beträgt:  {result}")
    time.sleep(5)



