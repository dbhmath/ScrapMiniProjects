# -*- coding: utf-8 -*-
"""
Created on Mon Sep 3 02:37:34 2019

@author: dbhmath
"""
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

def delete_content_codemirror(AC,driver,element):
    AC(driver)\
        .move_to_element(element) \
        .click() \
        .key_down(Keys.CONTROL)\
        .send_keys("a") \
        .key_up(Keys.CONTROL)\
        .key_down(Keys.DELETE)\
        .key_up(Keys.DELETE)\
        .perform()

def get_df_from_query(query, driver):
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.CodeMirror")))
    #element =  driver.find_element(By.CSS_SELECTOR, "div.CodeMirror")
    delete_content_codemirror(ActionChains,driver,element)
    ActionChains(driver) \
        .move_to_element(element) \
        .click() \
        .send_keys(query) \
        .perform() 
    #time.sleep(1)
    ActionChains(driver)\
        .key_down(Keys.CONTROL)\
        .key_down(Keys.RETURN)\
        .key_up(Keys.RETURN)\
        .key_up(Keys.CONTROL)\
        .perform()
    time.sleep(1)
    try:
        data =  driver.find_element(By.CLASS_NAME ,"result-table").get_attribute("outerHTML")
        df = pd.read_html(data)[0]
    except:
        df = pd.DataFrame()
    
    return df

def use_selenium(url,q):
    options = webdriver.ChromeOptions()

    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    #options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    driver.get(url)

#     q = """ F = πEats.name,	Eats.pizza,	Frequents.pizzeria(Eats⨝Frequents⨝Serves)
#     UPDATE = π Eats.name,	Eats.pizza(F)
#     Eats - (UPDATE∩Eats) """
#     q = "PC"


    d = get_df_from_query(q,driver)

    print(d)

    driver.close()


# Window openend one and maximized
def use_selenium_list(url,queries):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    driver.get(url)
    df_list = list()
    for q in queries:
        d = get_df_from_query(q,driver)
        print(d)
        df_list.append(d)

    driver.close()
    return df_list

# Window openend one and maximized
def grade_selenium_list(url,queries,qnums):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    
    grades = list()
    l = read_solution()
    
    log = list()
    
    for i,q in zip(qnums,queries):
        g=0
        correcto = False
        df1 = get_df_from_query(q,driver)
        #if df1 != None:
        df2 = l[i-1]
        obs =''
        print("Pregunta:",i)
        print(q)
        
        if df1.shape == df2.shape:
            df1.columns = df2.columns.values
            
            df1=df1.round(decimals = 3)
            df2=df2.round(decimals = 3)
            
            df10 = df1.sort_values(by=df1.columns.tolist()).reset_index(drop=True)
            df20 = df2.sort_values(by=df2.columns.tolist()).reset_index(drop=True)
            print("------Resultado:-----")
            print(df10)
            print("------Solucion:------")
            print(df20)
            print("---------------------")
            correcto = df20.equals(df10)
            
            
            #print(df1.compare(df2, keep_equal=True))         
            g = 1 if correcto else 0
        else:
            print (df1.shape, df2.shape)
            obs = 'R:'+str(df2.shape)+'/ E:'+str(df1.shape)
        
        
        print( "Correcto?:", correcto)
        print("---------------------")
        
        if df1.shape == (0,0):
            obs = 'query error'
        
      
        grades.append(g)
        log.append(obs)

    driver.close()
    return grades,log


def write_df_resp(df_list, file):
    writer = pd.ExcelWriter(file)
    
    for i, df in enumerate(df_list):
        df.to_excel(writer,sheet_name='q'+str(i+1))
    writer.save() 

def create_solution():
    #url = "https://dbis-uibk.github.io/relax/calc/gist/7d1871f79a8bcb4788de/uibk_db_pizza/0"
    url = "https://dbis-uibk.github.io/relax/calc/local/uibk/local/3"
    #use_selenium(url)
    xfile = 'solucion_pizza'
    sname = 'questions'
    df = pd.read_excel(xfile+'.xlsx', sheet_name=sname)
    print(df)
    
    df_list = use_selenium_list(url,df['query'].to_list())
    #print(df_list)
    write_df_resp(df_list, xfile+'_df.xlsx')
    
def read_solution():
    xfile = 'solucion_pizza_df'
    xfile = 'solucion_compu_df'
    lista = list()
    for i in range(1,16):
        df = pd.read_excel(xfile+'.xlsx', sheet_name='q'+str(i),index_col=0)
        lista.append(df)
    return lista


if __name__ == '__main__':
    #url = "https://dbis-uibk.github.io/relax/calc/gist/7d1871f79a8bcb4788de/uibk_db_pizza/0"
    url = "https://dbis-uibk.github.io/relax/calc/local/uibk/local/3"
    #use_selenium(url)
    xfile = 'RespuestasEnviadas'
    sname = 'respuestas'
    df = pd.read_excel(xfile+'.xlsx', sheet_name=sname)
    print(df)
    
    dff = df[['q','email']]
    dff['grades'], dff['obs']= grade_selenium_list(url,df['query'].to_list(),df['q'].to_list())
    
    print(dff)
    writer = pd.ExcelWriter("Calificacion.xlsx")
    dff.to_excel(writer,sheet_name='grades')
    writer.save()
    
    
    