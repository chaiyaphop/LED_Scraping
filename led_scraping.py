from datetime import date, datetime
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import time


def find_n_page(urls, civils):
    # Set up the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(
            options=options
        )
    
    # Find the number of page
    n_page = {}
    for i, url in enumerate(urls):
        driver.get(url)
        find_n_page = driver.find_element(by=By.XPATH, value='/html/body/table[3]/tbody/tr/td[1]/table[2]/tbody/tr/td[2]/div')
        page_nums = list(find_n_page.text.split('/'))[1]
        n_page[civils[i]] = int(page_nums)
    driver.quit()

    return n_page

def scrape_data(urls, n_page, output_dir, output_filename):
    # Set up the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(
            options=options
        )

    # Scrape data
    data_dict = {}
    for i, c in enumerate(n_page):
        data_list = []
        url = urls[i]
        for page in range(1, int(n_page[c])+1):
            sub_url = f'{url}&page={page}'
            driver.get(sub_url)
            time.sleep(0.5)
            try:
                for tr in range(3, 53):
                    tr_onclick = driver.find_element(by=By.XPATH, value=f'/html/body/table[3]/tbody/tr/td[1]/table[1]/tbody/tr[2]/td/table/tbody/tr[{tr}]')
                    tr_onclick.click()
                    time.sleep(1)
                    
                    result_windows = driver.window_handles[1]
                    driver.switch_to.window(result_windows)

                    for a in range(1, 7):
                        result_url = driver.current_url
                        land_deeds = driver.find_element(by=By.XPATH, value='/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[5]/td/font')
                        land_deed = land_deeds.text
                        subdistricts = driver.find_element(by=By.XPATH, value='/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td[1]/font')
                        subdistrict = subdistricts.text
                        districts = driver.find_element(by=By.XPATH, value='/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td[2]/font')
                        district = districts.text
                        provinces = driver.find_element(by=By.XPATH, value='/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[7]/td/font')
                        province = provinces.text
                        land_areas = driver.find_element(by=By.XPATH, value='/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[8]/td[2]')
                        land_area = land_areas.text
                        land_owners = driver.find_element(by=By.XPATH, value='/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[9]/td[1]/font')
                        land_owner = land_owners.text
                        sale_methods = driver.find_element(by=By.XPATH, value='/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[18]/td/font')
                        sale_method = sale_methods.text
                        appraised_prices = driver.find_element(by=By.XPATH, value='/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[20]/td/font')
                        appraised_price = appraised_prices.text
                        appointment_numbers = driver.find_element(by=By.XPATH, value=f'/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[17]/td/table/tbody/tr[{a}]')
                        appointment_number = appointment_numbers.text.split(' ')[1]
                        appointment_dates = driver.find_element(by=By.XPATH, value=f'/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[17]/td/table/tbody/tr[{a}]/td[1]/font')
                        appointment_date = appointment_dates.text
                        statuss = driver.find_element(by=By.XPATH, value=f'/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[2]/table/tbody/tr[17]/td/table/tbody/tr[{a}]/td[2]')
                        status = statuss.text
                        try:
                            maps_imgs = driver.find_element(by=By.XPATH, value='/html/body/table/tbody/tr[3]/td/div/table/tbody/tr/td[3]/table/tbody/tr[4]/td/div/a/img[@src]')
                            maps_img = maps_imgs.get_attribute('src')
                        except:
                            maps_img = '-'

                        data = {
                            'URL': result_url,
                            'ที่ดินโฉนดเลขที่': land_deed,
                            'แขวง/ตำบล': subdistrict,
                            'เขต/อำเภอ': district,
                            'จังหวัด': province,
                            'เนื้อที่': land_area,
                            'ผู้ถือกรรมสิทธิ์': land_owner,
                            'จะทำการขายโดย': sale_method,
                            'ราคาประเมินของเจ้าพนักงานบังคับคดี': appraised_price,
                            'นัดที่': appointment_number,
                            'วันที่': appointment_date,
                            'สถานะ': status,
                            'แผนที่ตั้งทรัพย์': maps_img
                        }

                        data_list.append(data)
                    
                    driver.close()

                    home_windows = driver.window_handles[0]
                    driver.switch_to.window(home_windows)
                    time.sleep(0.1)
            except:
                None
        data_dict[c] = data_list

    # Write result file
    with pd.ExcelWriter(f'{output_dir}/{output_filename}') as writer:
        for data in data_dict:
            df = pd.DataFrame(data_dict[data])
            df.to_excel(writer, sheet_name=f'CIVIL_{data}', index=False)

    driver.quit()

    return data_dict


if __name__ == '__main__':
    start_time = datetime.now()
    print('Program start at %s' % start_time)

    # Define variables
    prefix = 'https://asset.led.go.th/newbid-old/asset_search_province.asp'
    asset_type_id = input('(str) Which asset type id do you want to scrape? 002 = ห้องชุด, 003 = ที่ดินพร้อมสิ่งปลูกสร้าง ')
    province = input('(str) Which province do you want to scrape? bkk = กรุงเทพ, spk = สมุทรปราการ, pte = ปทุมธานี')
    urls = []
    if province == 'bkk':
        province_id = '%A1%C3%D8%A7%E0%B7%BE' # กรุงเทพ
        # Select BKK civil
        civils = []
        while True:
            civil = input('(int) Which BKK civil do you want to scrape? type "e" to exit. ')
            if civil == 'e':
                break
            else:
                civils.append(int(civil))
        print(f'Civil {civils}')
        for civil in civils:
            sub_province_code = f'%E1%BE%E8%A7%A1%C3%D8%A7%E0%B7%BE%C1%CB%D2%B9%A4%C3%20{civil}'
            url = f'{prefix}?search_asset_type_id={asset_type_id}&search_province={province_id}&search_sub_province={sub_province_code}'
            urls.append(url)
    elif province == 'spk':
        province_code = '%CA%C1%D8%B7%C3%BB%C3%D2%A1%D2%C3' # สมุทรปราการ
        civils = [0]
        print(f'Civil {civils}')
        url = f'{prefix}?search_asset_type_id={asset_type_id}&search_province={province_code}'
        urls.append(url)
    elif province == 'pte':
        province_code = '%BB%B7%D8%C1%B8%D2%B9%D5' # ปทุมธานี
        civils = [0]
        print(f'Civil {civils}')
        url = f'{prefix}?search_asset_type_id={asset_type_id}&search_province={province_code}'
        urls.append(url)
    print(urls)

    # Find number of page
    n_page = find_n_page(urls, civils)

    # Scrape data
    # # Define variables
    output_dir = 'Projects/led_scraping/output'
    gen_date = (datetime.now()).strftime('%Y%m%d')
    output_filename = f'LED_{province}_{asset_type_id}_SCRAPING_{gen_date}.xlsx'

    _ = scrape_data(urls, n_page, output_dir, output_filename)

    end_time = datetime.now()
    print('Program end at : ', end_time)
    print('Completed in %s seconds' % (end_time - start_time).seconds)
