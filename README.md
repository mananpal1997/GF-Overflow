# Github-Feed-Overflow
POC (maybe? ʘ‿ʘ) to fill up any user's github feed with spam activities. You can also hide your actual activities by generating noise over your actual acitivities using this script.

## Story Time
Recently, a friend of mine ran a bot to star and fork some repos. In no time, my github acitivity feed was full of her activites. I scrolled to bottom of my feed, and I could see nothing else but activities of hers. ᕙ(⇀‸↼‶)ᕗ

> I was like dear god, why'd you do it!?  щ（ﾟДﾟщ）

Github's feed is not like Facebook's endless feed, you hit an end soon! After a short dialogue about this with one of the people from Github, I came to know that the activity feed you see on your dashboard is actually just a snapshot of events, so you can do nothing (for now) once it's created. Doesn't matter even if you unfollow or block that user. (╯°□°）╯︵ ┻━┻

## Conclusion
I came up with a Proof-Of-Concept to take advantage of this problem and abuse the system in a legit way. You can spam any user present on the github. To spam somone who follows you is really easy. To spam someone who doesn't follow you, Github API is used to get subscribed repos of the user. The script stars all the repos of the user, creates issues on subscribed repos, and also mentions user in comments and body of the issues. Though, this totally depends on how much subscriptions a user has, and thus may limit the spam. But hey! Atleast we tried, and it works perfectly for your followers. (☞ﾟヮﾟ)☞

Anyone who would like to test it is welcome. Although it's a one-time-fun to test it, after which you'll probably be unfollowed or blocked by others, isn't it cool (spam 🠘🠚 cool, maybe not :P)? And you can always apologize to friends for small spams    ( ͡° ͜ʖ ͡°)

Generate API token [here](https://github.com/settings/tokens) with repo, user and write:discussion access.
```
$ python git_spam.py --help
  usage: git_spam.py [-h] [--target_user USER2SPAM] --token TOKEN --username
                     USERNAME [--activities ACTIVITIES]
                     [--issues ISSUE_PER_REPO] [--mode MODE]
$ python git_spam.py --username <username> --token <token> --target_user <user_to_spam>
```

> After your mass acitvities, snapshots have been generated for target user(s). Now say, you think "Damn, I had starred inportant things, but now it's full of random repos as well". Well, there's a rollback option, that unstars all the repos that were starred during the spam.

![](http://i3.kym-cdn.com/photos/images/newsfeed/001/176/251/4d7.png)

##### Evil Plans
Generate accounts from mail-clients like [protonmail](https://protonmail.com), [tutanota](https://tutanota.com) etc, and make a giant "spam-mesh" with a thread spawned for each user token. (⌐■_■)