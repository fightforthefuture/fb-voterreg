from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from main.views import SafariView

urlpatterns = patterns(
    "main.views",
    url(r"^$", "index", name="index"),
    url(r"^fetch_me$", "fetch_me", name="fetch_me"),
    url(r"^fetch_friends$", "fetch_friends", name="fetch_friends"),
    url(r"^register$", "register", name="register"),
    url(r"^register_widget$", "register_widget", name="register_widget"),
    url(r"^pledge$", "pledge", name="pledge"),
    url(r"^submit_pledge$", "submit_pledge", name="submit_pledge"),
    url(r"^actually_registered$", "im_actually_registered", name="actually_registered"),
    url(r"^wont_vote$", "wont_vote", name="wont_vote"),
    url(r"^invite_friends$", "invite_friends", name="invite_friends"),
    url(r"^fetch_updated_batches$", "fetch_updated_batches", name="fetch_updated_batches"),
    url(r"^mark_batch_invited$", "mark_batch_invited", name="mark_batch_invited"),
    url(r"^unregistered_friends_list$", "unregistered_friends_list", name="unregistered_friends_list"),
)

urlpatterns += patterns(
    "",
    url(r"^voterreg_invite$", 
        TemplateView.as_view(template_name="voterreg_invite.html"), 
        name="voterreg_invite"),
    url(r"^safari$",
        SafariView.as_view(),
        name="safari"
    ),
)
