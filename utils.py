

def get_user_id(current_user):
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = 0
    return user_id
