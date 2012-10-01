$(function() {
    function requestCallback(response) {
        if (response) {
            _gaq.push(["_trackPageview", "/friends_invited"]);
        }
    }

    $(".invite-friends").click(function() {
        _gaq.push(["_trackPageview", "/show_invite_friends"]);
        FB.ui(
            {
                method: 'apprequests',
                message: 'The 2012 election is almost here-- join my voting network to see which of our friends are registered to vote!'
            }, requestCallback);
        return false;
    });
});