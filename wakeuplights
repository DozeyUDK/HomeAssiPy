import time
import logging
from miio import Device, DeviceException
#Xiaomi yeelight bulb morning ligts/wake up ligts - Dozey


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bulbs = [
    {"ip": "IP_ADRESS", "token": "INSERT_TOKEN_HERE"},
    {"ip": "IP_ADRESS", "token": "INSERT_TOKEN_HERE"},
]

def turn_on_bulb(bulb):
    """Włącz żarówkę, jeśli jest wyłączona."""
    try:
        device = Device(bulb['ip'], bulb['token'])
        status = device.send("get_prop", ["power", "bright"])
        power_status = status[0]
        if power_status == "off":
            logger.info(f"Żarówka {bulb['ip']} jest wyłączona. Włączam...")
            result = device.send("set_power", ["on"])
            if result == ["ok"]:
                logger.info(f"Żarówka {bulb['ip']} została włączona.")
            else:
                logger.warning(f"Nie udało się włączyć żarówki {bulb['ip']}")
        else:
            logger.info(f"Żarówka {bulb['ip']} już jest włączona.")
    except DeviceException as e:
        logger.error(f"Błąd połączenia z {bulb['ip']}: {e}")

def set_brightness(bulb, brightness):
    """Ustaw jasność żarówki."""
    try:
        device = Device(bulb['ip'], bulb['token'])
        result = device.send("set_bright", [brightness])
        if result == ["ok"]:
            logger.info(f"Ustawiono jasność {bulb['ip']} na {brightness}%")
        else:
            logger.warning(f"Nie udało się ustawić jasności na {bulb['ip']}")
    except DeviceException as e:
        logger.error(f"Błąd połączenia z {bulb['ip']}: {e}")

def morning_light(bulbs, total_time=600, steps=100):
    """Zwiększaj jasność do 100% przez określony czas."""
    logger.info(f"Rozpoczynam symulację porannego światła na {len(bulbs)} żarówkach")

    # Najpierw upewnij się, że wszystkie żarówki są włączone
    for bulb in bulbs:
        turn_on_bulb(bulb)

    # Obliczaj czas oczekiwania między krokami
    wait_time = total_time / steps  # Czas w sekundach na każdy krok
    brightness_increment = 100 / steps  # Przyrost jasności na każdy krok

    # Zwiększaj jasność stopniowo
    for step in range(steps + 1):
        brightness = int(step * brightness_increment)  # Ustaw jasność
        logger.info(f"Ustawiam jasność na {brightness}% ({step}/{steps})")
        for bulb in bulbs:
            set_brightness(bulb, brightness)
        time.sleep(wait_time)  # Odczekaj odpowiedni czas między krokami
    logger.info("Symulacja zakończona!")

if __name__ == "__main__":
    morning_light(bulbs, total_time=600, steps=100)
