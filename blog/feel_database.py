from blog import *

first_user_id, last_user_id = User.feel_bd(1000)
first_session_id, last_session_id = Session.feel_db(first_user_id, last_user_id)
Blog.feel_bd(first_session_id, 100)

first_post_id, last_post_id = Post.feel_db(10000)

Comment.feel_db(100000, first_user_id, last_user_id, first_post_id, last_post_id)
