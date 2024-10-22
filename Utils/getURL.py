from Utils.mid_to_id import mid_to_id


def getHomeUrl(user_id):
    return f'https://weibo.com/u/{user_id}'


def getUserUrl(user_id):
    return f'https://weibo.com/ajax/profile/info?uid={user_id}'


def getFriendUrl(user_id):
    return f'https://weibo.com/ajax/friendships/friends?page=1&uid={user_id}'


def getFansUrl(user_id):
    return f'https://weibo.com/ajax/friendships/friends?relate=fans&page=1&uid={user_id}&type=all&newFollowerCount=0'


def getBlogInfoUrl(mid):
    return f'https://weibo.com/ajax/statuses/show?id={mid}&locale=zh-CN'


def getCommentUrl(user_id, mid):
    blog_id = mid_to_id(mid)
    return blog_id,f'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={blog_id}&is_show_bulletin=2&is_mix=0&count=10&uid={user_id}&fetch_level=0&locale=zh-CN'
