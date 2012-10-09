$(function() {
    function requestCallback(response) {
        if (response) {
            _gaq.push(["_trackPageview", "/friends_invited"]);
            _kmq.push(["record", "Invited friends"]);
        }
        $.getJSON(SINGLE_USER_INVITED_URL);
    }

    $(".invite-friends, header ul li a.invite").click(function() {
        _gaq.push(["_trackPageview", "/show_invite_friends"]);
        _kmq.push(["record", "Opened friend invite dialog"]);
        FB.ui(
            {
                method: 'send',
                name: 'Vote. And help me get all our friends to vote.',
                link: FACEBOOK_CANVAS_PAGE
            },
            requestCallback);
        return false;
    });
});
