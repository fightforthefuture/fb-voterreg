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
                method: 'send',
                name: 'Vote. And help me get all our friends to vote.',
                link: VOTERREG_INVITE_URL
            },
            requestCallback);
        return false;
    });
});