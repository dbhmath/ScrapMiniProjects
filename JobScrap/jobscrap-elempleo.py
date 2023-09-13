import time
import sys
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

def show_results(driver,index=0):
    ### Mostrar 20 resultados
    dropdown = Select(driver.find_element(By.ID, "ResultsByPage"))
    dropdown.select_by_index(index)

def read_modal(driver,b):
    ### leer dialogo
    b.click()
    time.sleep(1)
    company=''
    salary=''
    city=''
    desc2=''
    desc1=''
    similarjobs=''
    time.sleep(1)
    try:        
        company = driver.find_element(By.CLASS_NAME, "company-name").text
        salary = driver.find_element(By.CLASS_NAME, "text-primary").text
        city = driver.find_element(By.CLASS_NAME, "info-city").text
        #publishdate=driver.find_element(By.CLASS_NAME, "pull-right info-publish-date")
        #time.sleep(delay)
        #wait = WebDriverWait(driver, 5)
        #wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'p')))
        #time.sleep(0.5)
        #more_review_data = driver.find_elements_by_css_selector("js-description p")
        description=driver.find_elements(By.CLASS_NAME, "js-description")
        desc1 = description[1].get_attribute("title")
        desc2 = description[1].text

        #description_p = driver.find_element(By.CSS_SELECTOR, 'p')
        #des = driver.find_element(By.XPATH,"[@class='js-description']")
        similarjobs = driver.find_element(By.CLASS_NAME, "ee-modal-equivalent-position").text.replace('Cargos relacionados\n', '')

    except:
        print("---------")
        print(company, salary, city, desc2, desc1, similarjobs, sep='\t')
        print("---------")
        pass
    #print("cierra")
    closebutton = driver.find_elements(By.CLASS_NAME, "close")
#    closebutton[5].click()

    print(company, salary, sep='\t')
    #WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-default.btn-sm#close[data-dismiss='modal']"))).click()
    for clbu in closebutton:
        try:
            clbu.click()
            #print(clbu.accessible_name,clbu.id)
        except:
            pass

    return [company, salary, city, desc2, desc1, similarjobs]

if __name__ == '__main__':
    delay = 1
    url = "https://www.elempleo.com/co/ofertas-empleo/?&trabajo=Estad%C3%ADstico"
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    #driver = webdriver.Chrome(driver_executable_path=ChromeDriverManager().install(), options=options)
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    driver.get(url)
    cookies = driver.find_elements(By.LINK_TEXT, "Aceptar cookies")
    cookies[0].click()
    time.sleep(delay)

    continuar = True
    df = pd.DataFrame(columns = ['Empresa', 'Salario', 'Ciudad', 'Descripcion1', 'Descripcion2', 'EmpleosSimilares'])
    jobs=0
    while continuar == True:
        show_results(driver,2)
        time.sleep(3)

        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        print(f"buttons={len(buttons)}")
         
        for b in buttons:
            if b.accessible_name==" Vista rápida":
                try:
                    lista = read_modal(driver,b)
                    df.loc[len(df)] = lista
                    jobs += 1
                    print(jobs)                    
                except:                    
                    input("Presione cualquier tecla para continuar")
            time.sleep(delay)    
        archivo = 'jobs_elempleo_'+str(jobs)+'.csv'
        df.to_csv(archivo,index=False, encoding='utf-8')
        print(f'----- Guardado en {archivo} -----')
        ### Siguente pagina
        try:
            nxt = driver.find_element(By.CLASS_NAME, "js-btn-next")        
            nxt.click()
            time.sleep(3)
            #continuar=True
        except:
            continuar=False