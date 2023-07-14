
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver 
import pandas as pd
import _thread,time
import sqlite3


browse_params=False

class Generic:
    browser, service = None, None

    # Initialise the webdriver with the path to chromedriver.exe
    def __init__(self, driver: str):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--disable-dev-shm-usage')
        self.service = Service(driver)
        if browse_params:
            self.browser=webdriver.Chrome()
            # self.browser = webdriver.Chrome(service=self.service)
        else:
            # chromedriver_path = '/usr/bin/chromedriver'
            # self.browser=webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=options)
            # self.browser=webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=options)
            # self.browser=webdriver.Chrome(executable_path='C:/Users/HAMZA/Downloads/chromedriver_win32/chromedriver.exe', options=options)
            self.browser= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.browser.maximize_window()

    def open_page(self, url: str):
        self.browser.get(url)

    def close_browser(self):
        self.browser.close()
        
    def add_input(self, by: By, value: str, text: str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)

    def click_button(self, by: By, value: str):
        button = self.browser.find_element(by=by, value=value)
        button.click()
        
        
Jan_columns=['Brand Label', 'Why is this medicine prescribed', 'What are the precautions to be followed', 'How should this medicine be used', 'How to store the medication and dispose it of after its use later', 'What are possible side effects of this medication', 'Drug Category/Class', 'List of brands']
Jan_df=pd.DataFrame(columns=Jan_columns)

print('Individual')


def pull(page):
    try:
        print(page)
        browser=Generic('./chrome_driver')
        browser.open_page(page)
        global Jan_df
        
        try:
            name=browser.browser.find_element(by=By.CLASS_NAME,value='DrugHeader__title-content___2ZaPo').text
        except:
            name=''
        try:
            manufac=browser.browser.find_element(by=By.CLASS_NAME,value='DrugHeader__meta-value___vqYM0').text
        except:
            manufac
        try:
            salt_name=browser.browser.find_element(by=By.CLASS_NAME,value='saltInfo').text
        except:
            salt_name=''
        try:
            prescription_name=browser.browser.find_element(by=By.CLASS_NAME,value='DrugHeader__prescription-req___34WVy').text
            if prescription_name=='Prescription Required':
                prescription_name='Yes'
            else:
                prescription_name='No'
        except:
            prescription_name='No'

        try:
            mrp=browser.browser.find_element(by=By.CLASS_NAME,value='DrugPriceBox__slashed-price___2UGqd').text.replace(' ','')
        except:
            try:
                mrp=browser.browser.find_element(by=By.CLASS_NAME,value='PriceBoxPlanOption__margin-right-4___2aqFt').text
            except:
                mrp=''
        try:
            best_price=browser.browser.find_element(by=By.CLASS_NAME,value='DrugPriceBox__price___dj2lv').text.replace(' ','')
        except:
            try:
                best_price=browser.browser.find_element(by=By.CLASS_NAME,value='PriceBoxPlanOption__offer-price___3v9x8').text
            except:
                best_price=''
        try:
            class_=browser.browser.find_elements(by=By.CLASS_NAME,value='DrugFactBox__flex___1bp8c')
            for c in class_:
                print(c.text)
                if 'Therapeutic Class' in class_.text:
                    class_=c.text.replace('Therapeutic Class','')
                    break
        except:
            class_=''

        elems=browser.browser.find_elements(by=By.CLASS_NAME,value='DrugHeader__meta___B3BcU')
        storage=''
        for elem in elems:
            if 'STORAGE' in elem.text:
                storage = elem.text.replace('STORAGE\n','')
                break
                

        elems=browser.browser.find_elements(by=By.CLASS_NAME,value='DrugOverview__container___CqA8x')
        introduction=''
        safety=''
        for elem in elems:
            if 'PRODUCT INTRODUCTION' in elem.text:
                introduction = elem.text.replace('PRODUCT INTRODUCTION\n','')
            elif 'SAFETY ADVICE' in elem.text:
                safety = elem.text.replace('SAFETY ADVICE\n','')


        list=[name,manufac,salt_name,prescription_name,storage,mrp,best_price,class_,introduction,safety,page]

        
        # new_row_df = pd.DataFrame([list], columns=Jan_df.columns)
        # Jan_df = Jan_df.append(new_row_df, ignore_index=True)
        # Jan_df.to_csv('Generic_brands.csv',index = False)
        browser.browser.close()
        while(1):
                try:
                    conn = sqlite3.connect('database.db')
                    cur = conn.cursor()
                    cur.execute('INSERT INTO data (name,manufac,salt_name,prescription_name,storage,mrp,best_price,class_,introduction,safety, link) values ("'+name+'","'+manufac+'","'+salt_name+'","'+prescription_name+'","'+storage+'","'+mrp+'","'+best_price+'","'+class_+'","'+introduction+'","'+safety+'","'+page+'")')

                    conn.commit()
                    conn.close()
                    break
                except:
                    time.sleep(0.5)
        status_list.pop(0)
        print('Total Success : ',page)
    except:
        print('Total Failed : ',page)
        browser.browser.close()
        status_list.pop(0)

status_list=['']
no_bro=30
# max=794

links_df=pd.read_csv('1mg1.csv')

list_rem=links_df['Links'].tolist()
print(len(list_rem))

while(len(status_list)!=0):
    if len(list_rem)>0:
        if len(status_list)<=no_bro:
            print(len(status_list))
            _thread.start_new_thread(pull,(list_rem[0],))
            status_list.append(list_rem[0])
            list_rem.pop(0)
