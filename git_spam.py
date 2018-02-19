import requests
import argparse
from time import ctime, sleep
import random
import json
import sys

# ToDO - Sleep temporarily in between to sync with rate-limiting of the API token
# We can leave that for now as we enjoy 5000 requests per hour
# Problem is with rate of unauthorized requests - 60 per hour
# Rather crawl and scrape data instead of API then for unauthentic requests? - The saga continues...


def get_random_repo_data(seed):
    # 30 results per query, so we will use pagination to get large number of
    # results
    req = requests.get(base_url + "/users?since=%d" % seed)
    users = req.json()

    batch = {}
    for user in users:
        username = user["login"]
        batch[username] = []
        print("[%s] Fetching repos of user %s ..." % (ctime(), username))
        req = requests.get(user["repos_url"])
        repos = req.json()
        for repo in repos:
            batch[username].append(repo["name"])
        print("[%s] Done fetching repos of user %s" % (ctime(), username))
        sleep(1)
    return batch


# POC of spamming any user present on github
# No matter if the user follows you or not
# To spam a user who doesn't follow you is a bit complicated
# We will get all the subscriptions
# We'll always send pr and open issue on the subscription
# If subscription repo belongs to user, we'll star it as well to maximise spam :D
# For now I'm being lazy, and so leaving out the pull request part :P
def start_spam(user, token, flag, activity_number, issues_count):
    global user_seed

    # this file will be used if user wants to rollback and undo all the
    # activities
    log_file = open("activity.log", "wb")

    # Check if user follows you, then you do random starring as well to do more spam
    new_flag = False
    if user is not None:
        req = requests.get(base_url + "/users/%s/following/%s" % (user, username))
        if req.status_code // 100 != 4:
            new_flag = True

    if flag or new_flag:
        while activity_number > 0:
            activity_number -= 30
            user_batch = get_random_repo_data(user_seed)
            for name, repos in user_batch.items():
                for repo in repos:
                    try:
                        req = requests.put(
                            base_url + "/user/starred/%s/%s" % (name, repo),
                            headers={"Authorization": "token %s" % token}
                        )

                        if req.status_code != 204:
                            print("[%s] Failed starring %s/%s" % (ctime(), name, repo))
                        else:
                            print("[%s] Starred %s/%s successfully" % (ctime(), name, repo))
                            log_file.write(base_url + "/user/starred/%s/%s\n" % (name, repo))
                    except Exception as err:
                        print(err)
                        print("[%s] Failed starring %s/%s" % (ctime(), name, repo))
                    sleep(1)
            user_seed += 30
    if not flag:
        while activity_number > 0:
            activity_number -= 30
            req = requests.get(base_url + "/users/%s/subscriptions" % user)
            subscriptions = req.json()
            for sub in subscriptions:
                name, repo = sub["full_name"].split("/")
                if name == user:  # we'll star this also
                    try:
                        req = requests.put(
                            base_url + "/user/starred/%s/%s" % (name, repo),
                            headers={"Authorization": "token %s" % token}
                        )

                        if req.status_code != 204:
                            print("[%s] Failed starring %s/%s" % (ctime(), name, repo))
                        else:
                            print("[%s] Starred %s/%s successfully" % (ctime(), name, repo))
                            log_file.write(base_url + "/user/starred/%s/%s\n" % (name, repo))
                    except Exception as err:
                        print(err)
                        print("[%s] Failed starring %s/%s" % (ctime(), name, repo))
                # making an issue
                default_issue = {
                    "title": "Need help with setting up the project.",
                    "body": "I'm getting some errors while trying to run it. @%s" % (name)
                }
                req = requests.get(base_url + "/repos/%s/%s/issues" % (name, repo))
                issues = req.json()[::-1]
                issues_to_post = []
                """
                Use below url to get older issues to troll :D
                New issues copied will be easily caught as spam
                https://api.github.com/repos/servo/servo/issues?since=YYYY-MM-DDTHH:MM:SSZ
                """
                if len(issues) < issues_count:
                    for _ in xrange(issues_count - len(issues)):
                        issues_to_post.append(default_issue)
                for idx, issue in enumerate(issues):
                    if len(issues_to_post) == issues_count:
                        break

                    issues_to_post.append({
                        "title": issue["title"],
                        "body": issue["body"] + "\n@%s, Can you help me out?" % name
                    })
                random.shuffle(issues_to_post)
                for issue in issues_to_post:
                	try:
                		req = requests.post(
                		    base_url + "/repos/%s/%s/issues" % (name, repo),
                		    data=json.dumps(issue),
                		    headers={"Authorization": "token %s" % token}
                		)

                		if req.status_code != 201:
                			print("[%s] Failed creating issue for %s/%s" % (ctime(), name, repo))
                			break
                		else:
                			print("[%s] Issue for %s/%s created successfully" % (ctime(), name, repo))
                	except Exception as err:
                		print(err)
                		print("[%s] Failed creating issue for %s/%s" % (ctime(), name, repo))
                		break
                	sleep(1)

    log_file.close()
    print("[%s] Spam Completed" % ctime())
    if mode == 'rollback':
        rollback(token)


def rollback(token):
    print("[%s] Peforming clean-up and starting unstarring process..." % ctime())
    with open("activity.log", "rb") as f:
        links = f.read()
    links = links.split("\n")[:-1]
    err_urls = []
    for link in links:
        cnt = 0
        idx = len(link) - 1
        while cnt < 2:
            idx -= 1
            if link[idx] == '/':
                cnt += 1
        name, repo = link[idx + 1:].split("/")
        try:
            req = requests.delete(link, headers={"Authorization": "token %s" % token})
            if req.status_code == 204:
                print("[%s] Successfully unstarred %s/%s" % (ctime(), name, repo))
            else:
                err_urls.append(link)
                print("[%s] Failed unstarring %s/%s" % (ctime(), name, repo))
        except Exception as err:
            err_urls.append(link)
            print(err)
            print("[%s] Failed unstarring %s/%s" % (ctime(), name, repo))
        sleep(0.5)
    print("[%s] Finished clean-up" % ctime())

    if err_urls:
        print("%d repos were left starred due to some failure." % len(err_urls))
        print("Please run the rollback again for the left repos or unstar them manually.")
        with open("activity.log", "wb") as f:
            f.write("\n".join(err_urls))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target_user', dest='user2spam')
    parser.add_argument('--token', dest='token', required=True)
    parser.add_argument('--username', dest='username', required=True)
    parser.add_argument('--activities', dest='activities', default=30, type=int)
    parser.add_argument('--issues', dest='issue_per_repo', default=1, type=int)
    parser.add_argument('--mode', dest='mode', default='normal')
    args = parser.parse_args()

    user2spam, token, username = args.user2spam, args.token, args.username
    activity_number, issues_count, mode = args.activities, args.issue_per_repo, args.mode

    user_seed = 1
    base_url = "https://api.github.com"
    all_followers = False

    if mode not in ["normal", "rollback", 'only-rollback']:
        raise("Correct Usage: --mode <normal|rollback|only-rollback>")

    req = requests.get("https://api.github.com/rate_limit", headers={"Authorization": "token %s" % token})
    if req.status_code // 100 == 4:
        raise("Something went wrong. Probably with your token.")

    if mode == "only-rollback":
        rollback(token)
        sys.exit(0)

    if user2spam is None:
        all_followers = True

    # if issues_count > 30:
        # print("[%s] Max issues per repo can be 30, setting to 30..." % ctime())
        # issues_count = 30

    print("[%s] Starting Spam..." % ctime())
    start_spam(user2spam, token, all_followers, activity_number, issues_count)
