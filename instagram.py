from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from webdriver_manager.chrome import ChromeDriverManager
import os
import csv
import dotenv
from essential_generators import DocumentGenerator

dotenv.load_dotenv()
USERNAME = os.environ.get('USER_NAME')
PASSWORD = os.environ.get('PASSWORD')


class InstagramBot:
    def __init__(self, email, password):
        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        self.browserProfile.add_argument('--headless')
        self.browser = webdriver.Chrome(ChromeDriverManager().install(), options=self.browserProfile)
        self.email = email
        self.password = password

    def signIn(self):
        self.browser.get('https://www.instagram.com/accounts/login/')

        time.sleep(3)
        emailInput = self.browser.find_elements_by_css_selector('form input')[0]
        passwordInput = self.browser.find_elements_by_css_selector('form input')[1]

        emailInput.send_keys(self.email)
        passwordInput.send_keys(self.password)
        passwordInput.send_keys(Keys.ENTER)
        time.sleep(2)

    def followWithUsername(self, username):
        self.browser.get('https://www.instagram.com/' + username + '/')
        time.sleep(2)
        followButton = self.browser.find_element_by_css_selector('button')
        if followButton.text != 'Following':
            followButton.click()
            time.sleep(2)
        else:
            print("You are already following this user")

    def unfollowWithUsername(self, username):
        self.browser.get('https://www.instagram.com/' + username + '/')
        time.sleep(2)
        followButton = self.browser.find_element_by_css_selector('button')
        if followButton.text == 'Following':
            followButton.click()
            time.sleep(2)
            confirmButton = self.browser.find_element_by_xpath('//button[text() = "Unfollow"]')
            confirmButton.click()
        else:
            print("You are not following this user")

    def getUserList(self, search_key):
        self.browser.get('https://www.instagram.com/')
        time.sleep(2)
        if self.browser.find_elements_by_css_selector('.aOOlW.HoLwm'):
            self.browser.find_element_by_css_selector('.aOOlW.HoLwm').click()
        search_input = self.browser.find_element_by_css_selector('.XTCLo.x3qfX')
        search_input.send_keys(search_key)
        time.sleep(1)
        searchList = self.browser.find_elements_by_css_selector('div.fuqBx a')
        new_links = []
        for search in searchList:
            user_link = search.get_attribute('href')
            new_links.append(user_link)
        return new_links

    def getUserData(self, user_link):
        self.browser.get(user_link)
        time.sleep(2)
        followersText = self.browser.find_element_by_css_selector('ul li a .g47SY').get_attribute('title').replace(',', '')
        if checkCount(followersText):
            print(followersText, user_link)
            name = self.browser.find_element_by_class_name('rhpdm').text.strip()
            image = self.browser.find_element_by_css_selector('.XjzKX img').get_attribute('src')
            line = [name, image, followersText, user_link]
            write_csv([line])

    def getUserFollowers(self, username, min_count):
        self.browser.get('https://www.instagram.com/' + username)
        followersLink = self.browser.find_element_by_css_selector('ul li a')
        followersLink.click()
        time.sleep(2)
        followersList = self.browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
        numberOfFollowersInList = len(followersList.find_elements_by_css_selector('li'))
        print(numberOfFollowersInList)
        exit()

        followersList.click()
        actionChain = webdriver.ActionChains(self.browser)
        while numberOfFollowersInList < min_count:
            actionChain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
            numberOfFollowersInList = len(followersList.find_elements_by_css_selector('li'))
            print(numberOfFollowersInList)

        followers = []
        for user in followersList.find_elements_by_css_selector('li'):
            userLink = user.find_element_by_css_selector('a').get_attribute('href')
            print(userLink)
            followers.append(userLink)
            if len(followers) == min_count:
                break
        return followers

    def closeBrowser(self):
        self.browser.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeBrowser()


def checkCount(num):
    try:
        if float(num) > 5000:
            return True
        return False
    except:
        return None


def generate_key():
    gen = DocumentGenerator()
    return gen.word()


def write_csv(lines):
    with open(file=file_name, encoding='utf-8', mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(lines)


def main():
    if os.path.isfile(file_name):
        os.remove(file_name)
    write_csv(head)
    bot = InstagramBot(USERNAME, PASSWORD)
    bot.signIn()
    while True:
        print('--------------- Started New Loop ---------------')
        if time.time() - start_time > 43200:
            break
        keyword = generate_key()
        print(keyword)
        links = bot.getUserList(keyword)
        for link in links:
            try:
                bot.getUserData(link)
            except:
                continue
        break


if __name__ == '__main__':
    file_name = 'Instagram.csv'
    head = [['NAME', 'IMAGE', 'FOLLOWERS', 'LINKS']]
    start_time = time.time()
    main()
