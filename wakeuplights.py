import time
import logging
from concurrent.futures import ThreadPoolExecutor
from miio import Device, DeviceException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bulbs = [
    {"ip": "191.168.0.123", "token": "insert_token1"},
    {"ip": "193.168.0.321", "token": "inser_token2"},
    {"ip": "194.168.0.987", "token": "insert_token3"},
]

def power_on(bulb):
    """Turn on the bulb."""
    try:
        device = Device(bulb['ip'], bulb['token'])
        device.send("set_power", ["on"])
        logger.info(f"Bulb {bulb['ip']} turned on")
    except DeviceException as e:
        logger.error(f"Error turning on bulb {bulb['ip']}: {e}")

def set_brightness(bulb, brightness):
    """Set the brightness of the bulb."""
    try:
        device = Device(bulb['ip'], bulb['token'])
        result = device.send("set_bright", [brightness])
        if result == ["ok"]:
            logger.info(f"Brightness of {bulb['ip']} set to {brightness}%")
        else:
            logger.warning(f"Failed to set brightness on {bulb['ip']}")
    except DeviceException as e:
        logger.error(f"Connection error with {bulb['ip']}: {e}")

def turn_on_all_bulbs_smoothly(bulbs):
    """Turn on all bulbs simultaneously and immediately set brightness to 1%."""
    logger.info("Turning on all bulbs simultaneously...")

    # Turn on all bulbs in parallel
    with ThreadPoolExecutor(max_workers=len(bulbs)) as executor:
        executor.map(power_on, bulbs)

    # Minimal wait to let devices register 'on' state
    time.sleep(0.1)  # was 0.3 → now ultra-fast

    # Set brightness to 1% simultaneously
    with ThreadPoolExecutor(max_workers=len(bulbs)) as executor:
        executor.map(lambda b: set_brightness(b, 1), bulbs)

    logger.info("All bulbs set to 1% brightness.")

def morning_light(bulbs, total_time=600, steps=100):
    """Gradually increase brightness to 100% over a specified time."""
    logger.info(f"Starting morning light simulation on {len(bulbs)} bulbs")

    # First, set all bulbs to 1% brightness
    turn_on_all_bulbs_smoothly(bulbs)

    wait_time = total_time / steps
    brightness_increment = 100 / steps

    for step in range(1, steps + 1):  # start from 1%
        brightness = int(step * brightness_increment)
        logger.info(f"Setting brightness to {brightness}% ({step}/{steps})")
        with ThreadPoolExecutor(max_workers=len(bulbs)) as executor:
            executor.map(lambda b: set_brightness(b, brightness), bulbs)
        time.sleep(wait_time)

    logger.info("Morning light simulation completed!")

if __name__ == "__main__":
    morning_light(bulbs, total_time=600, steps=100)
