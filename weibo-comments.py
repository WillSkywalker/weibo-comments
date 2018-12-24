from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from random import choice
import json
import os
import pickle

user_pages = (# 'https://weibo.com/bandaochenbao?profile_ftype=1&is_all=1#_0',
              # 'https://weibo.com/daliandaily?topnav=1&wvr=6&topsug=1&is_all=1',
              # 'https://weibo.com/dlwb?profile_ftype=1&is_all=1#_0',
              # 'https://weibo.com/huashangchenbao?profile_ftype=1&is_all=1#_0',
              # 'https://weibo.com/lswbwb?profile_ftype=1&is_all=1#_0',
              # 'https://weibo.com/rmrb?profile_ftype=1&is_all=1#_0',
              # 'https://weibo.com/p/1002061699258907/home?pids=&profile_ftype=1&is_all=1#_0',
              # 'https://weibo.com/p/1002062360016402/home?profile_ftype=1&is_all=1#_0',
              # 'https://weibo.com/qnsblh?profile_ftype=1&is_all=1#_0',
              'https://weibo.com/nddaily?profile_ftype=1&is_all=1#_0',
              'https://weibo.com/nfrb?profile_ftype=1&is_all=1#_0',
              'https://weibo.com/ycwb2010?profile_ftype=1&is_all=1#_0',
              'https://weibo.com/sunnews?profile_ftype=1&is_all=1#_0',
              'https://weibo.com/fjhxdb?profile_ftype=1&is_all=1#_0',
              'https://weibo.com/haidu?pids=&profile_ftype=1&is_all=1#_0',
              'https://weibo.com/wys5589999?profile_ftype=1&is_all=1#_0')
keywords = ('垃圾焚烧', '焚烧发电', '垃圾发电', 'PX')

chrome_options = Options()
chrome_options.add_argument('user-data-dir=selenium-weibo')
browser = webdriver.Chrome(chrome_options=chrome_options)



wait = ui.WebDriverWait(browser, 30)
browser.get(user_pages[0])


def login(username, password):
    # if os.path.isfile('kookies.pkl'):
    #     cookies = pickle.load(open('kookies.pkl', 'rb'))
    #     for cookie in cookies:
    #         browser.add_cookie(cookie)
        # return None
    wait.until(lambda browser: browser.find_element_by_xpath("//a[@node-type='loginBtn']"))
    browser.find_element_by_xpath("//a[@node-type='loginBtn']").click()
    wait.until(lambda browser: browser.find_element_by_xpath("//input[@name='username']"))
    user = browser.find_element_by_xpath("//input[@name='username']")
    user.clear()
    user.send_keys(username)
    psw = browser.find_element_by_xpath("//input[@name='password']")
    psw.clear()
    psw.send_keys(password)
    browser.find_element_by_xpath("//div[@node-type='login_frame']/div[6]/a").click()  # 点击“登录”
    try:
        wait.until(lambda browser: browser.find_element_by_xpath("//div[@node-type='layoutContent']"))
        browser.find_element_by_xpath("//div[@node-type='verifycode_box']")
        browser.save_screenshot('screenshot.png')
        code = input('Open screenshop.png and input verify code: ')
        vc = browser.find_element_by_xpath("//input[@name='verifycode']")
        vc.clear()
        vc.send_keys(code)
        browser.find_element_by_xpath("//div[@node-type='login_frame']/div[6]/a").click()
        sleep(5)
        # pickle.dump(browser.get_cookies(), open('kookies.pkl', 'wb'))
    except NoSuchElementException:
        pass


def search(keyword, url, name):
    browser.get(url)
    wait.until(lambda browser: browser.find_element_by_xpath("//span[@class='WB_search_s']"))
    searchbox = browser.find_element_by_xpath("//span[@class='WB_search_s']/form/input")
    searchbox.clear()
    searchbox.send_keys(keyword)
    try:
        browser.find_element_by_xpath("//span[@class='WB_search_s']/form/span/a").click()
    except:
        browser.get('https://www.weibo.com/{0}?topnav=1&wvr=6&topsug=1&is_all=1&is_search=1&key_word={1}'.format(name, keyword))
    return find_comments()


def find_comments():
    data = {}
    wait.until(lambda browser: browser.find_element_by_xpath("//div[@node-type='feed_nav']"))
    weibos = browser.find_elements_by_xpath("//div[@node-type='feed_list_content']")
    data = [weibo.text for weibo in weibos]
    comms = []
    buttons = browser.find_elements_by_xpath("//div[@node-type='feed_list_options']/div/ul/li[3]/a")
    # print(weibos)
    # print(buttons)
    for button in buttons:
        # print(button)
        button.click()
    # wait.until(lambda browser: browser.find_elements_by_xpath("div[@node-type='feed_list_commentListNum']"))
    sleep(5)
    # import pdb; pdb.set_trace()
    links = list(map(lambda x: x.get_attribute('href').replace('.com/', '.cn/'),
                browser.find_elements_by_xpath("//div[@node-type='feed_list_commentList']/a")))
    for link in links:
        comms.append(load_comments(link))
    return dict(zip(data, comms))


def load_comments(url):
    comments = []
    # temp_browser = webdriver.Chrome()
    browser.get(url)
    try:
        while True:
            comms = browser.find_elements_by_xpath("//div[@class='c']/span[@class='ctt']")
            for c in comms:
                comments.append(c.text)
            nextpage = browser.find_element_by_xpath("//div[@id='pagelist']/form/div/a")
            if nextpage.text != '下页':
                break
            else:
                browser.get(nextpage.get_attribute('href'))
    except NoSuchElementException:
        pass
    return comments


def main():
    data = {}
    # login('name@address.com', '*********')
    for user_page in user_pages:
        name = user_page.split('?')[0][18:].replace('/', '-')
        data[name] = {}
        for keyword in keywords:
            data[name][keyword] = search(keyword, user_page, name)
        json.dump(data, open('%s.json' % name, 'w', encoding='utf8'), sort_keys=True, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
