import praw
from praw.models import MoreComments
import requests
import json
import os
import sys
from time import sleep
import credentials

if len(sys.argv) != 3:
    print("Please enter in the form: python3 archiver.py <subreddit> <number of posts>")
    quit()
else:
    subreddit = sys.argv[1]
    numPosts = int(sys.argv[2])




# sets up reddit credentials
reddit = praw.Reddit(
    client_id = credentials.client_id,
    client_secret = credentials.client_secret,
    user_agent= credentials.user_agent
)



# sets the base path for your where you will save stuff
basePath = credentials.basePath


# gets the url of the media, provided that the input post is has either an image or a video
def get_media_url(postID):
    outURL = f'https://www.reddit.com/{postID}/.json'
    r = requests.get(outURL,headers={'User-agent':credentials.user_agent})
    out = r.json()

    path = out[0]['data']['children'][0]["data"]

    if path["is_video"]:
        return path["secure_media"]["reddit_video"]["fallback_url"].split("?source")[0]
    else:
        return path["url_overridden_by_dest"]


# saves the media to the current directory (probably can fix later, I think the current way isn't great)
def save_media(postId):
    url = get_media_url(postId)
    os.system(f"wget -U \"{credentials.user_agent}\" -O \"{postId}.{url[-3:]}\" {url}")


#recursive function in order to save all of the comments in the original tree
#really proud of not messing up the recursion on this
def get_comments(comment): 
    
    if (len(comment.replies) == 0):
        return {
            "author" : get_author(comment.author),
            "body" : comment.body,
            "score" : comment.score 
            }
    
    tree = {}

    
    tree["author"]  = get_author(comment.author)
    tree["body"] = comment.body
    tree["score"] = comment.score

    children = {}
    for child in comment.replies:
        if isinstance(child, MoreComments):
            continue
        if len(child.replies) == 0:
            children[child.id] = {
                "author" : get_author(child.author),
                "body" : child.body,
                "score" : child.score
            }
        else:
            children[child.id] = {
                "children" : get_comments(child)
            }
    
    tree["children"] = children
    return tree

# gets the author of the comment/post, returns unknown if not available (probably deleted user or removed post)
# if I were better at this then I'd do what removeddit does
def get_author(redditor):
    if redditor != None:
        return redditor.name
    
    return "Unknown"

# brings it all together, saving the title, body, and comments
def save_post(postId):
    post = {}

    #gets title
    post["title"] = submission.title

    # gets author
    post["author"] = get_author(submission.author)

    # gets score
    post["score"] = submission.score
    
    #gets the body text of the post, or the url of the media
    if submission.is_self:
        post["body"] = submission.selftext 
    else:
        post["body"] = get_media_url(submission)

    # gets a dict of the comments in a tree
    comments = {}
    for topLevelComment in submission.comments:
        if isinstance(topLevelComment, MoreComments):
            continue
        comments[topLevelComment.id] = get_comments(topLevelComment)

    post["comments"] = comments

    return post

# changes to the base path specified by the user
os.chdir(basePath)

for submission in reddit.subreddit(subreddit).hot(limit=numPosts):
    if not submission.stickied:
        postId = submission.id

        #creates a new dir for post and changes to it
        print(f"Saving post with id: {postId}")
        os.makedirs(postId)
        os.chdir(basePath+"/"+postId)

        # saves dict object of the post's content
        post = save_post(postId)
        
        # saves the media  
        if not submission.is_self:
            save_media(postId)

        #writes to json
        with open(f"{postId}.json", "w") as f:
            json.dump(post, f)
            f.close()
        
        os.chdir(basePath)

        #kinda just clears the screen, not really needed 
        print("-------------------------------\n\n\n\n\n")


        #can be changed, I'm going better safe than sorry with API limits
        sleep(2)
