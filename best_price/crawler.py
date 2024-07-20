import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(r'C:\WebDrivers\chromedriver.exe')  # Update the path if needed
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def clear_cookies(driver):
    try:
        driver.delete_all_cookies()
        print("Cookies cleared.")
    except Exception as e:
        print(f"Failed to clear cookies: {e}")


def close_cookies_overlay(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-testid="cookies-overlay__container"]'))
        ).click()
    except Exception as e:
        print(f"Cookies overlay not found or could not be closed: {e}")


def get_products_from_page(driver):
    products = []
    try:
        product_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="l-card"]'))
        )
        for element in product_elements:
            try:
                link = element.find_element(By.CSS_SELECTOR, 'a.css-z3gu2d').get_attribute('href')
                title = element.find_element(By.CSS_SELECTOR, 'h6.css-1wxaaza').text
                price = ""
                try:
                    price = element.find_element(By.CSS_SELECTOR, 'p.css-13afqrm').text
                except:
                    print(f"Price not found for product with link: {link}")

                image_url = element.find_element(By.CSS_SELECTOR, 'img.css-8wsg1m').get_attribute('src')
                location_date_element = element.find_element(By.CSS_SELECTOR, 'p.css-1mwdrlh')
                location_date = location_date_element.text if location_date_element else ""

                products.append({
                    'link': link,
                    'title': title,
                    'price': price,
                    'image_url': image_url,
                    'location_date': location_date
                })
            except Exception as e:
                print(f"Error processing product element: {e}")
    except Exception as e:
        print(f"Error loading products: {e}")
    return products


def display_progress(current_page, total_pages, total_products):
    print(f"Page {current_page}/{total_pages} - Total Products: {total_products}")


def click_next_page(driver):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="pagination-forward"]'))
        )
        driver.execute_script("arguments[0].click();", next_button)
    except Exception as e:
        print(f"Failed to click next page button: {e}")


def get_all_products(base_url):
    driver = init_driver()
    all_products = []
    current_page = 1
    total_pages = 1  # Initialize total_pages with 1, to handle the first page

    try:
        driver.get(base_url)

        # Clear cookies before starting the scraping
        clear_cookies(driver)

        # Initial total pages calculation
        try:
            pagination_items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li[data-testid="pagination-list-item"]'))
            )
            total_pages = max(
                int(item.find_element(By.CSS_SELECTOR, 'a').text)
                for item in pagination_items
                if item.find_element(By.CSS_SELECTOR, 'a').text.isdigit()
            )
        except Exception as e:
            print(f"Error determining total pages: {e}")

        while current_page <= total_pages:
            # Close cookies overlay if present
            close_cookies_overlay(driver)

            # Extract products from the current page
            products = get_products_from_page(driver)
            all_products.extend(products)

            # Display progress update
            display_progress(current_page, total_pages, len(all_products))

            # Click the 'Next' button to go to the next page
            try:
                click_next_page(driver)
                current_page += 1
                time.sleep(8)  # Wait for the next page to load
            except Exception as e:
                print(f"No more pages or error: {e}")
                break
    finally:
        driver.close()
        driver.quit()

    return all_products


def save_to_json(data, filename='prices.json'):
    for i, product in enumerate(data, start=1):
        product['product_number'] = i

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"products": data}, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    base_url = "https://www.olx.ua/uk/list/q-powmr-6.2/?search%5Bfilter_float_price:from%5D=10000&search%5Bfilter_float_price:to%5D=40000"
    all_products = get_all_products(base_url)
    save_to_json(all_products)
    print(f"Successfully crawled and saved {len(all_products)} product links.")
