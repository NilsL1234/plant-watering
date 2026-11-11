from spidev import SpiDev
import time

spi = SpiDev()

# Chose SPI Bus 0 and CE (Chip select) 0.
# The MCP3008 is on the first bus and is the first chip (0,0). 
spi.open(0,0)

spi.max_speed_hz = 100_000

channel_mcp = 0

# read_channel: Sends a request to the mcp to measure. 3 Bytes are send. 
# Params: - spi: open spi object
#        - channel: on which channel the mcp reads the value
def read_channel(spi, channel):
    #Building the request: 
    # Byte 1: 00000001 (Startbit = 1, a valid request starts)
    # Byte 2: 10000000 (Single-Ended-Bit = 1, measure a single chanel relative to gnd; the next 3 bits tell the channel, so where to measure on the mcp: 000= CH0, 001=CH1...)
    # Byte 3: 00000000 (Dummy byte so the slave can answer on the clock, MOSI and MISO send at the same time!)
    # 
    request = [1, (8 + channel) << 4, 0]
    response = spi.xfer2(request)
    value = ((response[1] & 3)<< 8) | response[2]
    print(response) 
    return value

for i in range(1000):
    result = read_channel(spi, channel_mcp)
    print(f"Das Ergebnis der Messung {i+1} beträgt:  {result}")
    time.sleep(1)

spi.close()