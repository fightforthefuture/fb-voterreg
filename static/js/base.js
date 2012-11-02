$(function() {
    function requestCallback(response) {
        if (response) {
            _gaq.push(["_trackPageview", "/friends_invited"]);
            _kmq.push(["record", "Invited friends"]);
        }
        $.getJSON(SINGLE_USER_INVITED_URL);
    }

    // Makes an ajax request to fetch any new notifications, displaying the
    // new ones (and removing the old ones) if there are any new ones.
    //
    // This function is bound to the 'checkNotifications' event on the
    // window object. To manually fire, run this from anywhere:
    // $(window).trigger('checkNotifications');
    function checkNotifications(evt){
        $.get(NOTIFICATION_URL, function(data){
            if(!!data){
                var $notifications = $('.notification');
                $notifications.find('li').remove();
                $(data).appendTo($notifications);
            }
        });
    }
    $(window).bind('checkNotifications', checkNotifications);

    $('.voter').live('click', function(evt){
        evt.preventDefault();
        var $li = $(this).closest('li');
        $li.find('.years_voted').show();
    });

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
