from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime
import math

options = webdriver.ChromeOptions()
# options.add_argument("--window-size=1920,1080")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.implicitly_wait(0.5)
link = "https://finance.discuss.com.hk/forumdisplay.php?fid=57&filter=type&orderby=new_lastpost&ascdesc=DESC&typeid=1293"
driver.get(link)
time.sleep(2.5)

data = {"Date": [], "Comments": []}

for p in range(11, 21):
    if p > 0:
        link1 = f"{link}&page={p}"
        driver.get(link1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_post = soup.find_all(lambda tag: tag.name == 'tbody' and tag.get('class') == ['forumdisplay_thread'])
        # all_post = soup.find_all("tbody", attrs={"class":"forumdisplay_thread"})

        for h in all_post:
            url = f"https://finance.discuss.com.hk/{h.span.a.get('href')}"
            driver.get(url)

            ads_elems = driver.find_elements(By.CSS_SELECTOR,
                                             ".adsbygoogle.adsbygoogle-noablate[data-vignette-loaded=true]")
            if len(ads_elems) > 0:
                ActionChains(driver).move_by_offset(5, 5).click().perform()
                time.sleep(5)

            # login_elems = driver.find_elements(By.CSS_SELECTOR, ".maintable.wrap.discuss_regist_wapper login.discuss_regist_section")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            login_elems = soup.find("div", attrs={"class": "discuss_regist_section"})
            if login_elems != None:
                pass
                # driver.find_elements(By.CSS_SELECTOR, ".discuss_regist_section form input[name='username']")[0].send_keys(ID)
                # driver.find_elements(By.CSS_SELECTOR, ".discuss_regist_section form input[name='password']")[0].send_keys(password)
                # driver.find_elements(By.CSS_SELECTOR, ".discuss_regist_section form button[name='loginsubmit']")[0].click()
            else:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                head_comment = soup.find("meta", {"property": "og:description"})["content"]
                head_date = soup.find("div", attrs={"class": "post-date"}).text
                data["Date"].append(head_date)
                data["Comments"].append(head_comment)
                all_comments = soup.find("div", attrs={"class": "mainbox-container mb-t_msgfont"}).find_all("div",
                                                                                                            attrs={
                                                                                                                "class": "mainbox viewthread"})

                for c in all_comments:
                    if c.find("div", attrs={"class": "postmessage-content t_msgfont"}).find("span") == None:
                        pass
                    else:
                        if c.find("div", attrs={"class": "postmessage-content t_msgfont"}).find("span").find("div",
                                                                                                             attrs={
                                                                                                                 "class": "quote"}) != None:
                            normal_comments = c.find("div", attrs={"class": "postmessage-content t_msgfont"}).find(
                                "span")
                            unwanted = normal_comments.find("div", attrs={"class": "quote"})
                            unwanted.extract()
                            comment_date = c.find("div", attrs={"class": "post-date"}).text
                            data["Date"].append(comment_date)
                            data["Comments"].append(normal_comments.text)
                        elif c.find("div", attrs={"class": "postmessage-content t_msgfont"}).find("span").find("div",
                                                                                                               attrs={
                                                                                                                   "class": "quote"}) == None:
                            normal_comments = c.find("div", attrs={"class": "postmessage-content t_msgfont"}).find(
                                "span").text
                            comment_date = c.find("div", attrs={"class": "post-date"}).text
                            data["Date"].append(comment_date)
                            data["Comments"].append(normal_comments)

                exist_pages = soup.find("div", attrs={"class": "pagination-buttons"})

                driver.switch_to.default_content()

                if exist_pages == None:
                    pass
                else:
                    no_pages = math.ceil(
                        (int(soup.find("div", attrs={"class": "pagination-buttons"}).find("em").text)) / 15)
                    for i in range(no_pages + 1):
                        if i > 1:
                            # ads_elems = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.adsbygoogle.adsbygoogle-noablate[data-vignette-loaded=true]')))
                            ads_elems = driver.find_elements(By.CSS_SELECTOR,
                                                             ".adsbygoogle.adsbygoogle-noablate[data-vignette-loaded=true]")
                            if len(ads_elems) > 0:
                                ActionChains(driver).move_by_offset(5, 5).click().perform()
                                time.sleep(5)
                            url2 = f'{url}&page={i}'
                            driver.get(url2)
                            soup = BeautifulSoup(driver.page_source, 'html.parser')
                            all_comments = soup.find_all("div", attrs={"class": "postmessage-content t_msgfont"})
                            comment_date = soup.find_all("div", attrs={"class": "post-date"})
                            for c in all_comments:
                                if c.find("span") == None:
                                    data["Comments"].append("NA")
                                elif c.find("span").find("div", attrs={"class": "quote"}) != None:
                                    comment = c.find("span")
                                    unwanted = comment.find("div", attrs={"class": "quote"})
                                    unwanted.extract()
                                    data["Comments"].append(comment.text)
                                elif c.find("span").find("div", attrs={"class": "quote"}) == None:
                                    comment = c.find("span").text
                                    data["Comments"].append(comment)
                            for d in comment_date:
                                data["Date"].append(d.text)

                            driver.switch_to.default_content()