import string
import random
import time

import requests as req
from threading import Thread
import json
import logging

def gen_ran_str(s): return ''.join(random.choice(string.ascii_letters) for i in range(s))

with open("tester_conf.json", "r") as f:
    conf = json.load(f)

api_url = conf['api_url']
number_of_users = conf['number_of_users']
max_posts_per_user = conf['max_posts_per_user']
max_likes_per_user = conf['max_likes_per_user']

def create_user(login, password, username):
    resp = req.post(api_url + "/signup", json = {
        "login": login,
        "password": password,
        "username": username
    })

    if resp.status_code == 200: return resp.json()['token']
    elif resp.status_code == 409: raise ValueError
    else: raise Exception(resp.text)

def post_random_posts(session, max_num_to_post):

    to_post = random.randint(1, max_num_to_post)

    posted = []

    for i in range(to_post):
        resp = session.post(api_url + "/create_post", json = {
            "content": gen_ran_str(100)
        })

        if resp.status_code != 200:
            logging.error(f"{resp.status_code} {resp.text}")
        else:
            posted.append(resp.json())

    return posted

def like_posts(session, ids):

    liked = []

    for post_id in ids:
        resp = session.get(api_url + f"/post/{post_id}/like_post")

        if resp.status_code == 200:
            liked.append(post_id)
        elif resp.status_code == 404:
            logging.error(f"Post {post_id} not found")
        elif resp.status_code == 400:
            continue

    return liked

def perform_for_user():

    tries = 0

    login = gen_ran_str(20)
    password = gen_ran_str(20)
    username = gen_ran_str(20)

    while True:
        try:
            user_token = create_user(login, password, username)
        except ValueError:
            login = gen_ran_str(20)
            password = gen_ran_str(20)
            username = gen_ran_str(20)
        except Exception as e:
            logging.error(str(e))
            if tries > 5: return
            tries += 1
        else:
            break

    ses = req.session()

    ses.headers = {
        "Authentication": user_token
    }

    posted = post_random_posts(ses, max_posts_per_user)

    time.sleep(5)

    resp = ses.get(api_url + "/posts")

    if resp.status_code != 200:
        logging.error(f"{resp.status_code} {resp.text}")
        return

    posts_ids = resp.json()["posts"]
    posts_to_like = [random.choice(posts_ids) for _ in range(random.randint(1, max_likes_per_user))]

    liked = like_posts(ses, posts_to_like)

    resp = ses.post(api_url + "/logout", json = {"auth_token": user_token})

    if resp.status_code == 200: logging.warning(f"{login} DONE posted: {len(posted)}, liked: {len(liked)}")
    else: logging.error(f"{resp.status_code} {resp.text}")


users = []
for user_num in range(number_of_users):
    thread = Thread(target=perform_for_user, daemon=True)

    thread.start()

    users.append(thread)


for u in users: u.join()

print("DONE")