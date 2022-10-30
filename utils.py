
def order_title_alphabetically(posts):
    posts_title = []
    for post in posts:
        split_str = post.title
        if len(split_str.split("§")[1]) == 1:
            posts_title.append(post.title.replace("§", " 000"))
            continue
        if len(split_str.split("§")[1]) == 2:
            posts_title.append(post.title.replace("§", " 00"))
            continue
        if len(split_str.split("§")[1]) == 3:
            posts_title.append(post.title.replace("§", " 0"))
    posts_title.sort()
    posts_title = [title.replace(" 000", "§") for title in posts_title]
    posts_title = [title.replace(" 00", "§") for title in posts_title]
    posts_title = [title.replace(" 0", "§") for title in posts_title]
    return posts_title

