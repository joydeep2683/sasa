from utils import *
import logging



class KeywordToolIo(object):
    def __init__(self, source='keywordtool.io', country='US'):
        super(KeywordToolIo, self).__init__()
        self.source = source
        self.country = country


    def return_browser_object(self, url):
        options = Options()
        options.headless = True
        browser = webdriver.Chrome(options=options)
        browser.get(url)
        return browser

    def get_soup(self, browser_object):
        html_code = browser_object.page_source
        soup = BeautifulSoup(html_code, 'lxml')
        return soup


    def fetch(self, keyword):
        try:
            keyword = keyword.strip()
            options = Options()
            options.headless = True
            browser = webdriver.Chrome(options=options)
            browser.get('https://keywordtool.io/')
            time.sleep(10)
            element = browser.find_element_by_xpath("//input[@id='edit-keyword']")
            element.clear()
            element.send_keys(keyword)
            element.send_keys(Keys.RETURN)
            time.sleep(5)
            link_to_scrape = browser.current_url
            browser1 = self.return_browser_object(link_to_scrape)
            soup = self.get_soup(browser1)
            raw_rel_kw = soup.find_all(class_="form-textarea form-control hidden")[1].text.split('\n')
            browser.quit()
            xc = {'keyword': keyword, 'types':'rel_kw_wov', 'data':raw_rel_kw}
            logging.info("sucessfully_processed_keywordtoolio_tag:{}".format(keyword))
        except Exception as e:
            logging.error("exception_occurred_in_keywordtoolio_tag:{}".format(keyword), exc_info=True)
            return None
        if len(raw_rel_kw) > 1:
            return xc
