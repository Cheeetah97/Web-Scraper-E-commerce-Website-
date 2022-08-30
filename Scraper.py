from selenium import webdriver
import bs4 as bs
import pandas as pd
import time

driver = webdriver.Chrome('C:/Users/Shariq/Downloads/chromedriver_win32/chromedriver.exe')
driver.get('https://www.hepsiburada.com')
time.sleep(8)

# Category name and url
cat_element = driver.find_element_by_xpath('//div[@class="footer-middle-left"]')
cat_soup = bs.BeautifulSoup(cat_element.get_attribute('innerHTML'),'html.parser')
cat_soup = cat_soup.find_all("section")[1]
cat_soup = cat_soup.find_all("ul")[0]
cat_soup = cat_soup.find_all("a") 

final_df = pd.DataFrame()
for cat in cat_soup:
    
    # Category Selection
    driver.get(cat["href"]+"?sayfa=1")
    time.sleep(8)
    page_element = driver.find_element_by_xpath('//div[@class="pagination"]')
    page_soup = bs.BeautifulSoup(page_element.get_attribute('innerHTML'),'html.parser')
    if len(page_soup.find_all("a")) > 1:
        cat_total_pages = int(page_soup.find_all("a")[-1].text)
    else:
        cat_total_pages = int(page_soup.find_all("a")[0].text)
    
    for cat_page in range(1,cat_total_pages+1,1):
        driver.quit()
        driver = webdriver.Chrome('C:/Users/Shariq/Downloads/chromedriver_win32/chromedriver.exe')
        driver.get(cat["href"]+"?sayfa="+str(cat_page))
        time.sleep(8)
        prod_elements = driver.find_elements_by_xpath('//li[@class="search-item col lg-1 md-1 sm-1  custom-hover not-fashion-flex"]')
        prod_soups = []
        
        for prod_element in prod_elements:
            prod_soups.append(bs.BeautifulSoup(prod_element.get_attribute('innerHTML'),'html.parser'))
            
        for prod_soup in prod_soups:
            
            # Product name and url
            prod_soup_name = prod_soup.find("a").find("div", attrs={"class": "product-detail"}).find('h3')
            prod_soup_url = prod_soup.find("a")
            
            # Product Selection
            try:
                driver.get("https://www.hepsiburada.com"+prod_soup_url["href"]+"-yorumlari?sayfa=1")
                time.sleep(8)
                page_element2 = driver.find_element_by_xpath('//ul[@class="hermes-PaginationBar-module-3qhrm hermes-PaginationBar-module-1ujWo"]')
                page_soup2 = bs.BeautifulSoup(page_element2.get_attribute('innerHTML'),'html.parser')
                if len(page_soup2.find_all("span")) > 1:
                    total_review_pages = int(page_soup2.find_all("span")[-1].text)
                else:
                    total_review_pages = int(page_soup2.find_all("span")[0].text)
                marker = 0
            
            except:
                try:
                    driver.get("https://www.hepsiburada.com"+prod_soup_url["href"])
                    time.sleep(8)
                    total_review_pages = 1
                    marker = 1
                except:
                    continue
                    
            for prod_page in range(1,total_review_pages+1,1):
                
                if marker == 0:
                    driver.get("https://www.hepsiburada.com"+prod_soup_url["href"]+"-yorumlari?sayfa="+str(prod_page))
                    time.sleep(8)   
                else:
                    driver.get("https://www.hepsiburada.com"+prod_soup_url["href"])
                    time.sleep(8)  
                    
                spans = driver.find_elements_by_xpath('//div[@class="hermes-ReviewCard-module-34AJ_"]')
                
                date_lst = []
                name_lst = []
                city_lst = []
                review_lst = []
                rating_lst = []
                category = []
                product = []
                
                for span in spans:
                    print("Category = ",cat["title"])
                    category.append(cat["title"])
                    
                    print("Product = ",prod_soup_name["title"])
                    product.append(prod_soup_name["title"])
                    
                    soup = bs.BeautifulSoup(span.get_attribute('innerHTML'),'html.parser')
                    print("Date = ",soup.find("span", attrs={"itemprop": "datePublished"}).text)
                    date_lst.append(soup.find("span", attrs={"itemprop": "datePublished"}).text)
                    
                    print("Name = ",soup.find("span", attrs={"itemprop": "author"}).text)
                    name_lst.append(soup.find("span", attrs={"itemprop": "author"}).text)
                    
                    print("City = ",soup.find("span", attrs={"itemprop": "author"}).findNext("span").findNext('span').text)
                    city_lst.append(soup.find("span", attrs={"itemprop": "author"}).findNext("span").findNext('span').text)
                    
                    try:
                        print("Review = ",soup.find("span", attrs={"itemprop": "description"}).text)
                        review_lst.append(soup.find("span", attrs={"itemprop": "description"}).text)
                    except:
                        print("Review = No Review given")
                        review_lst.append('')
                    
                    print("Rating = ",len(soup.find_all('path', attrs={"fill": "#f28b00"})))
                    rating_lst.append(len(soup.find_all('path', attrs={"fill": "#f28b00"})))
                    print("###################################################")
                    
                df = pd.DataFrame(data={"Category":category,"Product":product,"Date":date_lst,"Name":name_lst,"City":city_lst,
                                        "Review":review_lst,"Rating":rating_lst})
                final_df = pd.concat([final_df,df])
                
final_df["City"] = final_df["City"].str.split("-",expand=True)[1]
final_df.to_csv("Scraped_Results_Final.csv",index=False)
driver.quit()
