#%%

print("Harap masukkan inputan, jika tidak diisi, maka pencarian akan dilakukan secara keseluruhan")
print("")
transmisi = input("Tipe Transmisi (Pilih 0 jika automatic. Pilih 1 jika manual): ")
penjual = input("Tipe Penjual (Pilih 0 jika diler. Pilih 1 jika individu): ")
tahun_min = input("Tahun Minimal (contoh=2010): ")
tahun_max = input("Tahun Maximal (contoh=2020): ")
harga_min = input("Harga Minimal (contoh=10000000): ")
harga_max = input("Harga Maximal (contoh=10000000): ")

opt = {} # inisialisasi dictionary

# menambahkan opsi transmisi
if transmisi == '0':
  opt['transmisi'] = 'automatic'
elif transmisi == '1':
  opt['transmisi'] = 'manual'

# menambahkan opsi penjual
if penjual == '0':
  opt['penjual'] = 'diler'
elif penjual == '1':
  opt['penjual'] = 'individu'

# menambahkan opsi tahun
if len(tahun_min)>0 and len(tahun_max)>0:
  opt['tahun_min_max'] = f"{tahun_min}_to_{tahun_max}"
elif len(tahun_min)>0:
  opt['tahun_min'] = tahun_min
elif len(tahun_max)>0:
  opt['tahun_max'] = tahun_max

# menambahkan opsi harga
if len(harga_min)>0 and len(harga_max)>0:
  opt['harga_min_max'] = f"{harga_min}_to_{harga_max}"
elif len(harga_min)>0:
  opt['harga_min'] = harga_min
elif len(harga_max)>0:
  opt['harga_max'] = harga_max

print("Kamu akan mencari berdasarkan: " + str(opt))
print("")

def mobil_bekas_search(opt):
  filter = ""
  if len(opt)>0:
    val = []
    if 'penjual' in opt:
      val.append(f"%2Cm_seller_type_eq_seller-type-{opt['penjual']}")

    if 'transmisi' in opt:
      val.append(f"%2Cm_transmission_eq_{opt['transmisi']}")
    
    if 'tahun_min' in opt:
      val.append(f"%2Cm_year_min_{opt['tahun_min']}")
    
    if 'tahun_max' in opt:
      val.append(f"%2Cm_year_max_{opt['tahun_max']}")
    
    if 'harga_min' in opt:
      val.append(f"%2Cprice_min_{opt['harga_min']}")
    
    if 'harga_max' in opt:
      val.append(f"%2Cprice_max_{opt['harga_max']}")
    
    if 'tahun_min_max' in opt:
      val.append(f"%2Cm_year_between_{opt['tahun_min_max']}")
    
    if 'harga_min_max' in opt:
      val.append(f"%2Cprice_between_{opt['harga_min_max']}")

    filter = filter.join(val)

    filter = "?filter=" + filter
  
  url = "https://www.olx.co.id/mobil-bekas_c198" + filter
  print(url)
  search(url)

def search(url):
  from bs4 import BeautifulSoup as bs
  import pandas as pd
  import time
  from selenium import webdriver
  from selenium.webdriver.common.by import By
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC
  from selenium.common.exceptions import TimeoutException

  PATH = "D:\Programming\Python\Scrapping\driver_selenium\chromedriver.exe"

  options = webdriver.ChromeOptions()
  options.add_argument('--ignore-certificate-errors')
  options.add_argument('--incognito')
  options.add_argument('--headless')
  options.add_argument('--no-sandbox')
  options.add_argument("start-maximized")
  driver = webdriver.Chrome(PATH, chrome_options=options)

  driver.get(url)
  print(driver.title)
  WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-aut-id=btnLoadMore]")))
  while True:
    try:
      WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-aut-id=btnLoadMore]"))).click()
      time.sleep(1) 
    except TimeoutException:
      break

  page_source = driver.page_source
  driver.quit()

  soup = bs(page_source, 'lxml')
  items = soup.find_all(attrs={"data-aut-id":"itemBox"})

  links = []
  titles = []
  prices = []
  years = []
  locations = []

  # looping
  for item in items:
      # title
      title_tag = item.find(attrs={"data-aut-id":"itemTitle"}).string.extract()
      titles.append(title_tag)

      # link
      a_tag = item.find('a').attrs['href']
      links.append(a_tag)

      # price
      price_tag = item.find(attrs={"data-aut-id":"itemPrice"}).string.extract()
      prices.append(price_tag)

      # year
      year_tag = item.find(attrs={"data-aut-id":"itemDetails"}).string.extract()
      years.append(year_tag)

      # location
      location_tag = item.find(attrs={"data-aut-id":"item-location"}).string.extract()
      locations.append(location_tag)

  d = {'title':titles, 'price':prices, 'year':years, 'location':locations, 'link':links}
  df = pd.DataFrame(d)
  df['price'] = df['price'].str.replace('.', '').str.replace('Rp ', '').astype(int)
  df['link'] = "https://www.olx.co.id" + df['link']
  df = df.drop_duplicates(['link']).reset_index(drop=True)
  df.to_csv("result_olx.csv", index=False)
  print("Done..! with total row = " + df.shape)

mobil_bekas_search(opt)