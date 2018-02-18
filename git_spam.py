import requests
import argparse
from time import ctime, sleep
import random
import json

# ToDO - Sleep temporarily in between to sync with rate-limiting of the API token


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
        sleep(2)
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

    if flag:
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
                            log_file.write(base_url + "/user/starred/%s/%s" % (name, repo))
                    except Exception as err:
                        print(err)
                        print("[%s] Failed starring %s/%s" % (ctime(), name, repo))
                    sleep(2)
            user_seed += 30
    else:
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
                            log_file.write(base_url + "/user/starred/%s/%s" % (name, repo))
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
                	sleep(2)

    log_file.close()
    print("[%s] Spam Completed" % ctime())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', dest='user')
    parser.add_argument('--token', dest='token', required=True)
    parser.add_argument('--activities', dest='activities', default=30, type=int)
    parser.add_argument('--issues', dest='issue_per_repo', default=1, type=int)
    args = parser.parse_args()

    user2spam, token, activity_number, issues_count = args.user, args.token, args.activities, args.issue_per_repo
    all_followers = False
    if user2spam is None:
        all_followers = True

    user_seed = 1
    base_url = "https://api.github.com"

    if issues_count > 30:
        print("[%s] Max issues per repo can be 30, setting to 30..." % ctime())

    print("[%s] Starting Spam..." % ctime())
    start_spam(user2spam, token, all_followers, activity_number, issues_count)