from locust import HttpUser, task, between
from random import randint


class WebsiteUser(HttpUser):
    wait_time = between(min_wait=1, max_wait=4)

    @task(weight=2)
    def view_articles(self):
        author_id = randint(1, 11)
        self.client.get(f"/blog/articles/?author_id={author_id}", name="/blog/articles")

    @task(weight=4)
    def view_article_detail(self):
        article_id = randint(1, 1000)
        self.client.get(f"/blog/articles/{article_id}", name="/blog/articles/:id")
