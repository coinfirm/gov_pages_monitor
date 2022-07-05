from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import requests
import json
import math
import random
import time
import datetime as DT

chromedriverPath = '/home/michal-lachowski/PycharmProjects/pythonProject/chromeDriver103/chromedriver'
s = Service(chromedriverPath)

driver = webdriver.Chrome(service=s)

added = False

keywords = ['crypto', 'cryptocurrency', 'crypto currency',
            'virtual currency', 'bitcoin', 'ethereum',
            'virtual asset', 'blockchain', 'TRM', 'distributed ledger',
            'ripple', 'stellar', 'avalanche',  'stable coin']

keywords2 = ['crypto', 'cryptocurrency', '"crypto currency"',
             '"virtual currency"', 'bitcoin', 'ethereum',
             '"virtual asset"', 'blockchain', 'TRM', '"distributed ledger"',
             'ripple', 'stellar', 'avalanche',  '"stable coin"']


def words_variation(word):

    virtual_asset = ['virtual asset', 'Virtual asset', 'Virtual Asset', 'VIRTUAL ASSET']
    virtual_currency = ['virtual currency', 'Virtual currency', 'Virtual Currency', 'VIRTUAL CURRENCY']
    crypto_currency = ['crypto currency', 'Crypto currency', 'Crypto Currency', 'CRYPTO CURRENCY']
    distributed_ledger = ['distributed ledger', 'Distributed ledger', 'Distributed Ledger', 'DISTRIBUTED LEDGER']
    stable_coin = ['stable coin', 'Stable coin', 'Stable Coin', 'STABLE COIN']
    if word == 'virtual asset':
        return virtual_asset, virtual_asset[0]
    elif word == 'virtual currency':
        return virtual_currency, virtual_currency[0]
    elif word == 'crypto currency':
        return crypto_currency, crypto_currency[0]
    elif word == 'distributed ledger':
        return distributed_ledger, distributed_ledger[0]
    elif word == 'stable coin':
        return stable_coin, stable_coin[0]
    else:
        return [], ""


def xpath(elem):

    url = f'https://www.instantmarkets.com/q/{elem}?ot=Bid%20Notification,Pre-Bid%20Notification,Award,Contract&pg=1&pdf=0-7&c=us&os=Active,Archived'
    page = requests.get(url)
    bs = BeautifulSoup(page.content, 'html.parser')
    dom = etree.HTML(str(bs))
    try:
        number = dom.xpath('//*[@class="ng-star-inserted"]/span/b[3]')[0].text
        return int(number)
    except:
        return False


def count_number_of_pages(number):

    return math.ceil(number / 10)


def instant_markets():
    keywords = ['crypto']
    global added
    for elem in keywords:
        number_of_articles = xpath(elem)
        number_of_pages = count_number_of_pages(number_of_articles)
        for page in range(number_of_pages):
            url = f'https://www.instantmarkets.com/q/{elem}?ot=Bid%20Notification,Pre-Bid%20Notification,Award,Contract&pg={page + 1}&pdf=0-7&c=us&os=Active,Archived'
            page = requests.get(url)
            bs = BeautifulSoup(page.content, 'html.parser')
            links = bs.findAll('a', class_='large default-text opptitle ng-star-inserted')
            word_list, word = words_variation(elem)
            list_of_links = []
            # if elem == word:
            for el in links:
                href = "https://www.instantmarkets.com" + str(el['href'])
                title = el['title']
                list_of_links.append([href, title])
            for link in list_of_links:
                driver.get(link[0])
                wait_for_content()
                content = driver.page_source
                content_low = content.lower()
                counter = 0
                if elem == word:
                    for w in word_list:
                        if content.find(w) > -1 and counter == 0:
                            counter += 1
                            print(content.lower())
                            if content_low.find("blockchain") > -1 or content_low.find("crypto ") > -1 or content_low.find("cryptocurrency") > -1 or content_low.find("crypto currency") > -1 or content.lower().find("distributed ledger") > -1:

                                added = True
                                payload = {
                                    "text": "New article found on https://www.instantmarkets.com/ with key word: " + elem + " ```" + "Title: " +
                                            link[1] + " \n" + "Link: "
                                            + link[0] + " ```"}
                                response = requests.post("https://hooks.slack.com/services/T14NAEEBZ/B038S999Y3W"
                                                         "/aee3kf3xwgnMr0Nq5jKxwXFW", json.dumps(payload))
                    else:
                        continue
                else:
                    if content_low.find("blockchain") > -1 or content_low.find("crypto ") > -1 or content_low.find(
                            "cryptocurrency") > -1 or content_low.find("crypto currency") > -1 or content.lower().find(
                            "distributed ledger") > -1:

                        added = True
                        payload = {
                            "text": "New article found on https://www.instantmarkets.com/ with key word: " + elem + " ```" + "Title: " +
                                    link[1] + " \n" + "Link: "
                                    + link[0] + " ```"}
                        response = requests.post("https://hooks.slack.com/services/T14NAEEBZ/B038S999Y3W"
                                                 "/aee3kf3xwgnMr0Nq5jKxwXFW", json.dumps(payload))
            # else:
            #     for el in links:
            #         href = "https://www.instantmarkets.com" + str(el['href'])
            #         title = el['title']
            #         content = driver.page_source
            #         if content.lower().find("blockchain") > -1 or content.lower().find(
            #                 "crypto") > -1 or content.lower().find("cryptocurrency") > -1 or content.lower().find(
            #                 "distributed ledger") > -1:
            #             payload = {
            #                 "text": "New article found on https://www.instantmarkets.com/ with key word: " + elem + " ```" + "Title: " +
            #                         title + " \n" + "Link: "
            #                         + href + " ```"}
            #             response = requests.post("https://hooks.slack.com/services/T14NAEEBZ/B038S999Y3W"
            #                                      "/aee3kf3xwgnMr0Nq5jKxwXFW", json.dumps(payload))


def wait_for_content():

    wait_time = random.randint(2, 6)
    time.sleep(wait_time)


def get_number_of_pages(text):

    first_split = text.split('(')
    sec_split = first_split[1].split(')')
    return sec_split[0]


def previous_week_date(number):

    today = DT.date.today()
    week_ago = today - DT.timedelta(days=number)
    year = str(week_ago.year)
    month = str(week_ago.month)
    day = str(week_ago.day)
    day_name = week_ago.strftime("%A")[0:3]
    month_name = week_ago.strftime("%B")
    month_name_short = week_ago.strftime("%b")
    return year, month, day, day_name, month_name_short, month_name


def ec_europa():

    global added
    year, month, day, day_name, month_name_short, month_name = previous_week_date(7)
    try:
        for elem in keywords:
            url = f'https://ec.europa.eu/commission/presscorner/advancedsearch/en?keywords={elem}&dotyp=&parea=&pareaType=&datepickerbefore=&datebefore=&commissioner=&datepickerafter={day}%20{month_name}%20{year}&dateafter={day_name}%20{month_name_short}%20{day}%20{year}%2000:00:00%20GMT%2B0200%20(Central%20European%20Summer%20Time)&pagenumber=1'

            driver.get(url)
            wait_for_content()
            number = driver.find_element(By.CLASS_NAME, "ecl-heading.ecl-heading--h2.ecl-u-mb-m")
            try:
                num = number.find_element(By.TAG_NAME, "span").text
                pages_number = get_number_of_pages(num)
                number_of_pages = count_number_of_pages(int(pages_number))
                for i in range(number_of_pages):
                    url2 = f'https://ec.europa.eu/commission/presscorner/advancedsearch/en?keywords={elem}&dotyp=&parea=&pareaType=&datepickerbefore=&datebefore=&commissioner=&datepickerafter={day}%20{month_name}%20{year}&dateafter={day_name}%20{month_name_short}%20{day}%20{year}%2000:00:00%20GMT%2B0200%20(Central%20European%20Summer%20Time)&pagenumber={i + 1}'
                    driver.get(url2)
                    wait_for_content()
                    by_class = driver.find_elements(By.CLASS_NAME, "ecl-link.ecl-list-item__link")
                    word_list, word = words_variation(elem)
                    list_of_links = []
                    if elem == word:
                        for ele in by_class:
                            href = ele.get_attribute('href')
                            title = ele.find_element(By.CLASS_NAME, "ecl-list-item__title.ecl-heading.ecl-heading--h3")
                            list_of_links.append([href, title.text])
                        for link in list_of_links:
                            driver.get(link[0])
                            wait_for_content()
                            content = driver.page_source
                            counter = 0
                            for w in word_list:
                                if content.find(w) > -1 and counter == 0:
                                    counter += 1

                                    added = True
                                    payload = {
                                        "text": "New article found on https://ec.europa.eu/ with key word: " + elem + " ```" + "Title: " +
                                                link[1] + " \n" +
                                                "Link: " + link[0] + " ```"}
                                    response = requests.post("https://hooks.slack.com/services/T14NAEEBZ/B038S999Y3W"
                                                             "/aee3kf3xwgnMr0Nq5jKxwXFW", json.dumps(payload))
                                else:
                                    continue

                    else:
                        for ele in by_class:
                            href = ele.get_attribute('href')
                            title = ele.find_element(By.CLASS_NAME, "ecl-list-item__title.ecl-heading.ecl-heading--h3")

                            added = True
                            payload = {
                                "text": "New article found on https://ec.europa.eu/ with key word: " + elem + " ```" + "Title: " + title.text + " \n" +
                                        "Link: " + href + " ```"}
                            response = requests.post("https://hooks.slack.com/services/T14NAEEBZ/B038S999Y3W"
                                                     "/aee3kf3xwgnMr0Nq5jKxwXFW", json.dumps(payload))

            except:
                continue

    except:
        return False

    driver.quit()


def last_7_days():

    list_of_days = []
    for days in range(7):
        year, month, day, day_name, month_name_short, month_name = previous_week_date(days)
        if int(day) < 10:
            day = day.replace("0", "")
        list_of_days.append([month_name_short, day, year])
    return list_of_days


def sam_gov():
    keywords2 = ['cryptocurrency']
    for elem in keywords2:
        url = f'https://sam.gov/search/?page=1&pageSize=25&sort=-modifiedDate&sfm%5Bstatus%5D%5Bis_active%5D=true&sfm' \
              f'%5BsimpleSearch%5D%5BkeywordRadio%5D=EXACT&sfm%5BsimpleSearch%5D%5BkeywordTags%5D%5B0%5D%5Bkey%5D={elem}' \
              f'&sfm%5BsimpleSearch%5D%5BkeywordTags%5D%5B0%5D%5Bvalue%5D={elem} '

        driver.get(url)
        wait_for_content()
        data_list = []
        try:
            page = driver.find_element(By.CLASS_NAME, 'sds-pagination__total').text.split(' ')
            page_number = page[1]
            count_of_ele = 0
            for number in range(int(page_number)):
                url2 = f'https://sam.gov/search/?page={number + 1}&pageSize=25&sort=-modifiedDate&sfm%5Bstatus%5D%5Bis_active%5D=true&sfm' \
                       f'%5BsimpleSearch%5D%5BkeywordRadio%5D=EXACT&sfm%5BsimpleSearch%5D%5BkeywordTags%5D%5B0%5D%5Bkey%5D={elem}' \
                       f'&sfm%5BsimpleSearch%5D%5BkeywordTags%5D%5B0%5D%5Bvalue%5D={elem} '

                driver.get(url2)
                wait_for_content()

                date = driver.find_elements(By.XPATH, '//*[@class="sds-field sds-field--stacked"]/div[2]/span')

                for i in date:
                    article_date = i.text.split(' ')
                    data_list.append([article_date[0], article_date[1].replace(',', ''), article_date[2]])
                title_html = driver.find_elements(By.TAG_NAME, "h3")
                for el in title_html:
                    try:
                        title = el.find_element(By.TAG_NAME, 'a')
                        href = title.get_attribute('href')
                        data_list[count_of_ele].append(title.text)
                        data_list[count_of_ele].append(href)
                        count_of_ele += 1
                    except:
                        continue

            last_days = last_7_days()
            for el in data_list:
                for single in last_days:
                    if el[0] == single[0] and el[1] == single[1] and el[2] == single[2]:
                        driver.get(el[4])
                        wait_for_content()
                        content = driver.page_source
                        content_low = content.lower()
                        if content_low.find("blockchain") > -1 or content_low.find("crypto ") > -1 or content_low.find(
                                "cryptocurrency") > -1 or content_low.find("crypto currency") > -1 or content.lower().find("distributed ledger") > -1:
                            global added
                            added = True
                            payload = {
                                "text": "New article found on https://sam.gov with key word: " + elem + " ```" + "Title: "
                                        + el[3] + " \n" + "Link: " + el[4] + " ```"}
                            response = requests.post("https://hooks.slack.com/services/T14NAEEBZ/B038S999Y3W"
                                                     "/aee3kf3xwgnMr0Nq5jKxwXFW", json.dumps(payload))

        except:
            continue


def ted_europa():

    global added
    for elem in keywords2:
        print(elem)
        url = 'https://ted.europa.eu/TED/search/search.do'
        driver.get(url)
        # driver.maximize_window()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            wait_for_content()
            driver.find_element(By.ID, 'clearAll').click()
            wait_for_content()
        except:
            try:
                wait_for_content()
                driver.find_element(By.ID, 'clearAll').click()
                wait_for_content()
            except Exception as e:
                print(e)
                print("clear fail")
                continue
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_for_content()
            driver.find_element(By.ID, 'textGroup').click()
            wait_for_content()
        except:
            try:
                driver.refresh()
                wait_for_content()
                driver.find_element(By.ID, 'clearAll').click()
                wait_for_content()
                driver.find_element(By.ID, 'textGroup').click()
                wait_for_content()
            except:
                print("text fail")
                continue
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_for_content()
            driver.find_element(By.ID, 'freeText').send_keys(elem)
            wait_for_content()
        except:
            try:
                wait_for_content()
                driver.find_element(By.ID, 'freeText').send_keys(elem)
                wait_for_content()
            except:
                print("text input fail")
                continue
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_for_content()
            driver.find_element(By.ID, 'businessOpportunitiesGroup').click()
            wait_for_content()
        except:
            try:
                wait_for_content()
                driver.find_element(By.ID, 'businessOpportunitiesGroup').click()
                wait_for_content()
            except:
                print("business fail")
                pass
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_for_content()
            driver.find_element(By.ID, 'dateGroup').click()
        except:
            try:
                wait_for_content()
                driver.find_element(By.ID, 'dateGroup').click()
            except:
                print("date fail")
                continue

        year, month, day, day_name, month_name_short, month_name = previous_week_date(7)
        if int(month) < 10:
            month = '0' + month
        if int(day) < 10:
            day = '0' + day
        date = f'{day}/{month}/{year}'
        wait_for_content()
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.find_element(By.ID, 'DOCUMENT_TYPE').send_keys("'Contract notice', 'Design contest'")
        except:
            print("Contract except")
            try:
                driver.find_element(By.ID, 'DOCUMENT_TYPE').send_keys("'Contract notice', 'Design contest'")
            except:
                print("Big contract except")
                pass
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_for_content()
            driver.find_element(By.ID, 'publicationDateFrom').send_keys(date)
        except:
            print("Date except")
            try:
                wait_for_content()
                driver.find_element(By.ID, 'publicationDateFrom').send_keys(date)
            except:
                print("Big date except")
                continue
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_for_content()
            driver.find_element(By.ID, 'dateGroup').click()
        except:
            print("Clicking date except")
            pass
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            wait_for_content()
            driver.find_element(By.ID, 'search').click()
        except:
            print("Search except")
            try:
                wait_for_content()
                driver.find_element(By.ID, 'search').click()
            except:
                print("Search except")
                try:
                    wait_for_content()
                    driver.find_element(By.ID, 'search').click()
                except:
                    print("Big search except")
                    continue
        try:
            driver.find_element(By.CLASS_NAME, 'page-icon.pagelast').click()
            wait_for_content()
            num = driver.find_element(By.CLASS_NAME, 'pager-number.page-number-selected')
            number_of_pages = int(num.text)
            wait_for_content()
            driver.find_element(By.CLASS_NAME, 'pagefirst.page-icon').click()

            for page in range(number_of_pages):
                wait_for_content()
                plus_button = driver.find_elements(By.CLASS_NAME, 'btn.btn-circle.btn-sm.show_hidden_col')
                wait_for_content()
                for button in plus_button:
                    wait_for_content()
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    button.click()
                    wait_for_content()

                wait_for_content()
                title = driver.find_elements(By.CLASS_NAME, 'bold.glyphicon-minus')
                list_of_titles = []
                list_of_hrefs = []
                for i, el in enumerate(title):
                    if i % 2 != 0:
                        list_of_titles.append(el.text)

                wait_for_content()
                for j in range(len(list_of_titles)):
                    href = driver.find_element(By.XPATH, f'//*[@id="notice"]/tbody/tr[{j * 2 + 1}]/td[2]/a')
                    list_of_hrefs.append(href.get_attribute('href'))
                wait_for_content()
                for index in range(len(list_of_titles)):
                    driver.get(list_of_hrefs[index])
                    wait_for_content()
                    content = driver.page_source
                    content_low = content.lower()
                    if content_low.find("blockchain") > -1 or content_low.find("crypto ") > -1 or content_low.find(
                            "cryptocurrency") > -1 or content_low.find("crypto currency") > -1 or content.lower().find(
                        "distributed ledger") > -1:
                        added = True
                        payload = {
                            "text": "New article found on  https://ted.europa.eu with key word: " + elem + " ```" + "Title: "
                                    + list_of_titles[index] + " \n" + "Link: " + list_of_hrefs[index] + " ```"}
                        response = requests.post("https://hooks.slack.com/services/T14NAEEBZ/B038S999Y3W"
                                                 "/aee3kf3xwgnMr0Nq5jKxwXFW", json.dumps(payload))
                wait_for_content()
                driver.find_element(By.CLASS_NAME, 'page-icon.pagenext').click()

        except NoSuchElementException:

            wait_for_content()
            plus_button = driver.find_elements(By.CLASS_NAME, 'btn.btn-circle.btn-sm.show_hidden_col')

            for button in plus_button:
                print("I was here", elem)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                wait_for_content()
                button.click()
                wait_for_content()

            wait_for_content()
            title = driver.find_elements(By.CLASS_NAME, 'bold.glyphicon-minus')
            list_of_titles = []
            list_of_hrefs = []
            for i, el in enumerate(title):
                if i % 2 != 0:
                    list_of_titles.append(el.text)

            wait_for_content()
            for j in range(len(list_of_titles)):
                href = driver.find_element(By.XPATH, f'//*[@id="notice"]/tbody/tr[{j * 2 + 1}]/td[2]/a')
                list_of_hrefs.append(href.get_attribute('href'))
            wait_for_content()

            for index in range(len(list_of_titles)):
                driver.get(list_of_hrefs[index])
                wait_for_content()
                content = driver.page_source
                content_low = content.lower()
                if content_low.find("blockchain") > -1 or content_low.find("crypto ") > -1 or content_low.find(
                        "cryptocurrency") > -1 or content_low.find("crypto currency") > -1 or content.lower().find(
                    "distributed ledger") > -1:
                    added = True
                    payload = {
                        "text": "New article found on  https://ted.europa.eu with key word: " + elem + " ```" + "Title: "
                                + list_of_titles[index] + " \n" + "Link: " + list_of_hrefs[index] + " ```"}
                    response = requests.post("https://hooks.slack.com/services/T14NAEEBZ/B038S999Y3W"
                                             "/aee3kf3xwgnMr0Nq5jKxwXFW", json.dumps(payload))


def coe():
    global added
    for elem in keywords2:
        print(elem)
        results = []
        # url = f'https://publicsearch.coe.int/#k={elem}#f=%5B%5D#dfd=7'
        # driver.get(url)
        for word in keywords2:
            if elem != word:
                wait_for_content()
                url = f'https://publicsearch.coe.int/#k=ALL({elem}, {word})#f=%5B%5D#dfd=7'
                driver.get(url)
                wait_for_content()
                titles = driver.find_elements(By.CLASS_NAME, "ms-srch-item-link")
                # wait_for_content()
                for el in titles:
                    title = el.get_attribute('title')
                    print(title)
                    href = el.get_attribute('href')
                    print(href)
                    results.append(title)
                    results.append(href)
        results = list(dict.fromkeys(results))
        print(results)
        if len(results) > 0:
            for i in range(0, len(results), 2):
                added = True
                payload = {
                    "text": "New article found on  https://www.coe.int/ with key word: " + elem + " ```" + "Title: "
                            + results[i] + " \n" + "Link: " + results[i+1] + " ```"}
                response = requests.post("https://hooks.slack.com/services/T14NAEEBZ/B038S999Y3W"
                                         "/aee3kf3xwgnMr0Nq5jKxwXFW", json.dumps(payload))
                wait_for_content()


if __name__ == '__main__':
    instant_markets()
    sam_gov()
    ted_europa()
    coe()
    ec_europa()
    if not ec_europa():
        ec_europa()

    if added == False:
        payload = {
            "text":  " ```" + "No article have matched the requirements. Nothing to show" + " ```"}
        response = requests.post("https://hooks.slack.com/services/T14NAEEBZ/B038S999Y3W"
                                 "/aee3kf3xwgnMr0Nq5jKxwXFW", json.dumps(payload))
    driver.quit()
