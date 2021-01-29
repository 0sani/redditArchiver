# Reddit Archiver

This is a project that can help archive subreddits. When run, it will take the x most recent posts (sorted by hot), and save both the post and the comment tree. Each post saved will be saved in a directory, with post's media (if any), and a json of the post.
The format of the json of the post is:

```json
{
    "title" : "the title of the post",
    "author" : "the author of the post",
    "body" : "Either text or media URL",
    "score" : "upvote count",
    "comments" : {
        "COMMENT_ID" : {
            "author" : "comment author",
            "body" : "comment body",
            "score" : "comment upvote count",
            "cildren" : {

            }
        }
    }

}
```
The children of the comment will be in the same format, and recurse until there are no more children.

## Requirements
A reddit application, with the client id, client secret, and a user agent
You will also need to install praw, which can be done with `pip3 install praw`

## Running
The program can be run using `python3 archiver.py <subreddit> <numPosts>`, where you replace the \<subreddit> with the subreddit, and the \<numPosts> with the number of posts you want to save

