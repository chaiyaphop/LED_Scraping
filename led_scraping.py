import logging
import os
import pandas as pd
import time
from contextlib import contextmanager
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from tqdm import tqdm
from typing import List, Dict


# Configuration and Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()


@contextmanager
def get_driver(headless: bool = True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        driver.quit()


def find_total_pages(urls: List[str], civil_codes: List[int]) -> Dict[int, int]:
    page_counts = {}
    with get_driver() as driver:
        for idx, url in enumerate(urls):
            driver.get(url)
            try:
                page_info = driver.find_element(by=By.XPATH, value='/html/body/table[3]/tbody/tr/td[1]/table[2]/tbody/tr/td[2]/div')
                page_nums = int(page_info.text.split('/')[1])
            except Exception as e:
                logging.error(f"Failed to parse total pages for URL: {url} | Error: {e}")
                page_nums = 0
            civil = civil_codes[idx]
            page_counts[civil] = page_nums
            logging.info(f"Civil {civil}: {page_counts[civil]} pages found")
    return page_counts


def scrape_properties(urls, n_pages, output_dir, output_filename):
    result = {}

    with get_driver() as driver:
        for idx, civil in enumerate(tqdm(n_pages, desc="All Civils", unit="civil")):
            logging.info(f"Scraping civil {civil}...")

            civil_data = []
            url = urls[idx]
            total_pages = int(n_pages[civil])

            for page in tqdm(range(1, total_pages + 1), desc=f'CIVIL {civil}', unit='page'):
                full_url = f'{url}&page={page}'
                driver.get(full_url)
                try:
                    for tr_idx in range(3, 53):
                        try:
                            row = driver.find_element(by=By.XPATH, value=f'/html/body/table[3]/tbody/tr/td[1]/table[1]/tbody/tr[2]/td/table/tbody/tr[{tr_idx}]')
                            row.click()

                            driver.switch_to.window(driver.window_handles[1])
                            time.sleep(0.5)

                            def get_text(xpath):
                                try:
                                    return driver.find_element(by=By.XPATH, value=xpath).text.strip()
                                except:
                                    logging.warning(f"Text not found for row {tr_idx}, civil {civil}")
                                    return "-"
                            
                            def get_image(xpath):
                                try:
                                    return driver.find_element(by=By.XPATH, value=xpath).get_attribute('src')
                                except:
                                    logging.warning(f"Map image not found for row {tr_idx}, civil {civil}")
                                    return "-"

                            for a in range(1, 7):
                                data = {
                                    'URL': driver.current_url,
                                    'ที่ดินโฉนดเลขที่': get_text('/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[5]/td/font'),
                                    'แขวง/ตำบล': get_text('/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td[1]/font'),
                                    'เขต/อำเภอ': get_text('/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td[2]/font'),
                                    'จังหวัด': get_text('/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[7]/td/font'),
                                    'เนื้อที่': get_text('/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[8]/td[2]'),
                                    'ผู้ถือกรรมสิทธิ์': get_text('/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[9]/td[1]/font'),
                                    'จะทำการขายโดย': get_text('/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[18]/td/font'),
                                    'ราคาประเมินของเจ้าพนักงานบังคับคดี': get_text('/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[20]/td/font'),
                                    'นัดที่': get_text(f'/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[17]/td/table/tbody/tr[{a}]').split(' ')[1],
                                    'วันที่': get_text(f'/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[17]/td/table/tbody/tr[{a}]/td[1]/font'),
                                    'สถานะ': get_text(f'/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[17]/td/table/tbody/tr[{a}]/td[2]'),
                                    'แผนที่ตั้งทรัพย์': get_image('/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[3]/table/tbody/tr[4]/td/div/a/img[@src]')
                                }

                                civil_data.append(data)

                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        except WebDriverException as e:
                            logging.warning(f"Skip row {tr_idx} due to error: {e}")
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                except WebDriverException as e:
                    logging.warning(f"Cannot find page {page} for civil {civil}: {e}")
                    continue

            result[civil] = civil_data

    # Save to Excel
    os.makedirs(output_dir, exist_ok=True)
    with pd.ExcelWriter(os.path.join(output_dir, output_filename)) as writer:
        for civil, records in result.items():
            df = pd.DataFrame(records)
            df.to_excel(writer, sheet_name=f'CIVIL_{civil}', index=False)

    return result


if __name__ == '__main__':
    start_time = datetime.now()
    logging.info(f"Program started at {start_time}")

    # User Input
    prefix = 'https://asset.led.go.th/newbid-old/asset_search_province.asp'
    asset_type_id = os.getenv('ASSET_TYPE_ID') or input('Asset type id (002 = ห้องชุด, 003 = ที่ดินพร้อมสิ่งปลูกสร้าง): ')
    asset_type = 'condo' if asset_type_id == '002' else 'house'
    province = os.getenv('PROVINCE') or input('Province (bkk = กรุงเทพ, spk = สมุทรปราการ, pte = ปทุมธานี): ').lower()

    civils, urls = [], []
    if province == 'bkk':
        province_code = '%A1%C3%D8%A7%E0%B7%BE'
        civils_str = os.getenv('CIVILS')
        if civils_str:
            civils = [int(c) for c in civils_str.split(',')]
        else:
            while True:
                civil = input('Which BKK civil? (type "e" to exit): ')
                if civil.lower() == 'e':
                    break
                civils.append(int(civil))
        for civil in civils:
            sub_province_code = f'%E1%BE%E8%A7%A1%C3%D8%A7%E0%B7%BE%C1%CB%D2%B9%A4%C3%20{civil}'
            url = f'{prefix}?search_asset_type_id={asset_type_id}&search_province={province_code}&search_sub_province={sub_province_code}'
            urls.append(url)
    else:
        if province == 'spk':
            province_code = '%CA%C1%D8%B7%C3%BB%C3%D2%A1%D2%C3'
        elif province == 'pte':
            province_code = '%BB%B7%D8%C1%B8%D2%B9%D5'
        civils = [0]
        urls.append(f'{prefix}?search_asset_type_id={asset_type_id}&search_province={province_code}')

    # Process
    n_pages = find_total_pages(urls, civils)
    output_dir = 'output'
    gen_date = datetime.now().strftime('%Y%m%d')
    output_filename = f'LED_SCRAPING_{province.upper()}_{asset_type.upper()}_{gen_date}.xlsx'
    scrape_properties(urls, n_pages, output_dir, output_filename)

    end_time = datetime.now()
    logging.info(f"Program completed in {(end_time - start_time).seconds} seconds")
