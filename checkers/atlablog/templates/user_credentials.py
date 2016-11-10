import random
import string


def generate_user_credentials(email=None):
    num_range = [str(i) for i in range(9)]
    letters = list(string.ascii_lowercase)
    user_suffix = random.sample(letters + num_range, 15)
    user_password = random.sample(num_range + letters, 24)
    user_email = random.sample(num_range + letters, 31)
    site_email = random.sample(num_range + letters, 5)

    user = "User_" + "".join(user_suffix)
    if not email:
        email = "".join(user_email) + "@" + "".join(site_email) + ".com"
    else:
        email += "@ructfe.flag"
    return user, "".join(user_password), email
