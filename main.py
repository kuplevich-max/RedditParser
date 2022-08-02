import re
from urllib import request

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
from uuid import uuid1

from pythonProject4.output_writers.file import FileWriter
from wait import post_count_is_enough
import json
import ssl

DOMAIN = 'https://www.reddit.com'
URL = 'https://www.reddit.com/top/?t=month'

DRIVER_PATH = '/Users/margo/ChromeDriver/bin/chromedriver'

class RedditParser:
    def __init__(self, url):
        self.portal = re.match('https://www\.[a-z0-9]+\.[a-z]+', url).group(0)
        self.driver = webdriver.Chrome(DRIVER_PATH)
        self.driver.get(url)
        self.posts = list()
        self.data_saver = FileWriter()


    def run(self):
        self.parse()
        self.save_retrieved_data()

    def __wait(self, post_count=100, seconds=120):
        enough_posts = False
        #make sure that we raise and catch the exception if enough posts aren't found or move the entire logic into the function itself
        while not enough_posts:
            enough_posts = post_count_is_enough(self.driver,
                                                (By.XPATH, '//div[@data-testid="post-container"]'),
                                                post_count)

    def parse(self):
        self.__wait(10, 10)
        html_doc = self.driver.page_source
        soup = BeautifulSoup(html_doc, 'xml')
        a = soup.find_all('a')
        post_urls = [f'{self.portal}{i.attrs["href"]}' for i in a
                     if i.attrs.get('data-click-id') == 'body']
        deltas = [datetime.timedelta(int(re.search(r'\d+', i.text).group(0)))
                  for i in a if i.attrs.get('data-click-id') == 'timestamp']
        post_dates = [(datetime.datetime.now() - delta).date().isoformat()
                      for delta in deltas]
        usernames = [i.text for i in a if re.match(r'u/', i.text)]
        user_urls = [f'{self.portal}{i.attrs["href"]}' for i in a
                     if re.match(r'u/', i.text)]
        span = soup.find_all('span')
        comments = [i.text for i in span if re.match('\d+\.\d+k\scomments',
                                                     i.text)]
        div = soup.find_all('div')
        votes = ([re.match(r'\d+k',i.text).group(0)
                  for i in div if re.match(r'\d+k', i.text)][::10])
        cats = [i.text for i in a
                if i.attrs.get('data-click-id') == 'subreddit' and i.text]
        users = list()
        for user_url in user_urls:
            users.append(self.parse_user(user_url))
        for i in range(len(post_urls)):
            if not all([post_urls[i], users[i].get('cake_day')]):
                continue
            self.posts.append(
                {
                    'id': uuid1().hex,
                    'url': post_urls[i],
                    'date': post_dates[i],
                    'username': usernames[i],
                    'comments': comments[i],
                    'votes': votes[i],
                    'category': cats[i],
                    'user_carma': users[i].get('user_carma'),
                    'comment_carma': users[i].get('comment_carma'),
                    'post_carma': users[i].get('post_carma'),
                    'cake_day': users[i].get('cake_day')
                }
            )

    def save_retrieved_data(self):
        for post in self.posts:
            self.data_saver.write_item(post)

        self.data_saver.flush()

    def parse_user(self, url):
        context = ssl._create_unverified_context()
        html_doc = request.urlopen(url, context=context).read()
        soup = BeautifulSoup(html_doc, 'xml')

        posts = soup.find(id="data")
        if posts is not None:
            posts_text = posts.text
        else:
            return

        json_string = re.findall(r'\{.+\}\};', posts_text)[0][:-1]
        data = json.loads(json_string)
        data = data['profiles']['about']
        user = dict()
        cake_day_tag = soup.find("span",
                                 id="profile--id-card--highlight-tooltip"
                                    "--cakeday")
        user['cake_day'] = cake_day_tag.text if cake_day_tag else ''
        if data:
            data = data.popitem()[1]['karma']
            user['post_carma'] = data['fromPosts']
            user['comment_carma'] = data['fromComments']
            user['user_carma'] = data['total']

        return user


RedditParser(URL).run()
