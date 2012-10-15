$(function() {
    function inviteFriendSucceeded(fbuid, $link) {
        // TODO: show loading animation in button
        $.getJSON(
            MARK_INVITED_URL,
            { "fbuid": fbuid },
            function() {
                var enclosingSpan = $link.parents("#friends li");
                enclosingSpan.find(".uninvited").hide();
                enclosingSpan.find(".invited").show();
            });
        var $prevUninv = $('#uninvited_friends').find('.num'),
            $prevInv = $('#invited_friends').find('.num');
        $prevUninv.text( parseInt($prevUninv.text(), 10) - 1);
        $prevInv.add('.score .invited .num').text( parseInt($prevInv.text(), 10) + 1);
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
        "click", "#friends li .btn",
        function(e) {
            inviteFriend($(this).parent().data("friend-fbuid"), $(this));
            return false;
        });

    $("#load_more_friends").click(function(e) {
        // TODO: show loading animation in button
        var $newDiv = $("<div/>").insertBefore(this);
        $newDiv.load(
            LOAD_MORE_URL,
            { "start": $("#friends li").length },
            function(){
                if(!$newDiv.text().replace(/\s+/gi, '').length){
                    $newDiv.remove();
                    $("#load_more_friends").remove();
                }
            });
        return false;
    });
});
