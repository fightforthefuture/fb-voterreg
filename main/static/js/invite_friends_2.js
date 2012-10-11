$(function() {
    function inviteFriendSucceeded(fbuid, $link) {
        // TODO: show loading animation in button
        $.getJSON(
            MARK_INVITED_URL,
            { "fbuid": fbuid },
            function() {
                var enclosingSpan = $link.parents(".friend_to_invite");
                enclosingSpan.find(".uninvited").hide();
                enclosingSpan.find(".invited").show();
            });
    }

    function inviteFriend(fbuid, $link) {
        FB.ui(
            {
                method: "send",
                to: fbuid,
                name: "Vote. And help me get all our friends to vote.",
                link: FACEBOOK_CANVAS_PAGE
            },
            function(response) {
                inviteFriendSucceeded(fbuid, $link);
            });
    }

    $(document).on(
        "click", ".friend_to_invite .invite",
        function(e) {
            inviteFriend($(this).parent().data("friend-fbuid"), $(this));
            return false;
        });

    $("#load_more_friends").click(function(e) {
        // TODO: show loading animation in button
        var $newDiv = $("<div/>");
        $("#friends").append($newDiv);
        $newDiv.load(
            LOAD_MORE_URL,
            { "start": $(".friend_to_invite").length });
        return false;
    });
});