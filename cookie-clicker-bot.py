from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import time

URL = "http://orteil.dashnet.org/experiments/cookie/"
COOKIE_ID = "cookie"
MONEY_ID = "money"
STORE_SELECTOR = "div#store b"

# Configure Chrome webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

# Locate the cookie element by ID
try:
    cookie = driver.find_element(By.ID, COOKIE_ID)
except exceptions.NoSuchElementException:
    print(f"Error: Element with ID '{COOKIE_ID}' not found.")
    driver.quit()
    exit()

def get_cookie_count():
    """Retrieve the current count of cookies."""
    try:
        return int(driver.find_element(By.ID, MONEY_ID).text.replace(",", ''))
    except exceptions.NoSuchElementException:
        print(f"Error: Element with ID '{MONEY_ID}' not found.")
        return 0

def click_button(button):
    """Locate and click on upgrade buttons."""
    try:
        id_ = f"buy{button}"
        upgrade_item = driver.find_element(By.ID, id_)
        upgrade_item.click()
        print(id_)
    except exceptions.NoSuchElementException:
        print(f"Error: Upgrade button '{button}' not found.")
    except exceptions.ElementClickInterceptedException:
        print(f"Error: Unable to click upgrade button '{button}'.")

upgrades_dict = {}

def get_upgrades():
    """Retrieve information about available upgrades."""
    all_prices = driver.find_elements(By.CSS_SELECTOR, STORE_SELECTOR)
    for item in all_prices:
        if item.text != '':
            try:
                upgrade_name = item.text.split("-")[0].strip()
                upgrade_price = item.text.split("-")[1].strip().replace(",", '')
                upgrades_dict.update({upgrade_name: int(upgrade_price)})
            except IndexError:
                print(f"Error: Unable to parse upgrade info '{item.text}'.")

def check_max_affordable_upgrade():
    """Check and return the highest affordable upgrade."""
    highest_price_can_get = 0
    highest_upgrade = None
    affordable_upgrades = {upgrade: price for upgrade, price in upgrades_dict.items() if money > price}

    # If there's only one affordable upgrade, choose it
    if len(affordable_upgrades) == 1:
        highest_upgrade = list(affordable_upgrades.keys())[0]
    else:
        # Choose the upgrade with the highest price among affordable ones
        for upgrade, price in affordable_upgrades.items():
            if price > highest_price_can_get:
                highest_price_can_get = price
                highest_upgrade = upgrade
        print("Affordable upgrades:", affordable_upgrades)
    return highest_upgrade


# Main Bot Loop (5 minutes)
start_time = time.time()
timeout = time.time() + 300

while time.time() < timeout:
    try:
        cookie.click()
    except exceptions.ElementClickInterceptedException:
        print("Error: Unable to click the cookie.")

    # Check for upgrades every 5 seconds
    if time.time() >= start_time + 5:
        get_upgrades()
        money = get_cookie_count()
        next_upgrade = check_max_affordable_upgrade()

        if next_upgrade is not None:
            click_button(next_upgrade)

        start_time = time.time()

    # Exit game when the time limit is reached and print cookies per second
    if time.time() >= timeout:
        try:
            cookie_per_second = driver.find_element(By.ID, "cps").text
            print(cookie_per_second)
        except exceptions.NoSuchElementException:
            print("Error: Element with ID 'cps' not found.")
        break

# driver.close()
