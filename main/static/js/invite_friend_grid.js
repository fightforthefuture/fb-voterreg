$(function() {
    function loadMoreButtonTop() {
        return $("#load_more_friends").offset().top - 
            $(document).scrollTop();
    }

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
                link: window['INVITE_LINK'] || window['SHARE_LINK'] || window['FACEBOOK_CANVAS_PAGE'],
                name: window['INVITE_NAME'] || "Vote. And help me get all our friends to vote.",
                description: window['INVITE_DESCRIPTION'],
                picture: window['INVITE_PICTURE']
            },
            function(response) {
                if (response && response["success"]) {
                    _kmq.push(["record", "individual invite"]);
                    inviteFriendSucceeded(fbuid, $link);
                }
            });
    }

    function messageFriend(fbuid) {
        FB.ui(
        {
            method: "send",
            to: fbuid,
            link: window['INVITE_LINK'] || window['SHARE_LINK'] || window['FACEBOOK_CANVAS_PAGE'],
            name: window['INVITE_NAME'] || "Vote. And help me get all our friends to vote.",
            description: window['INVITE_DESCRIPTION'],
            picture: window['INVITE_PICTURE']
        });
    }

    $(document).on(
        "click", "#friends li .invite",
        function(e) {
            inviteFriend($(this).parent().data("friend-fbuid"), $(this));
            return false;
        });

    $(document).on(
        "click", "#friends li .pledged",
        function(e) {
            messageFriend($(this).parent().data("friend-fbuid"));
            return false;
        });

    function loadMoreFriends() {
        if ($("#loading_label").is(":visible")) {
            return
        }
        $("#load_more_label").hide();
        $("#loading_label").show();
        var $newDiv = $("<div/>").insertBefore($("#load_more_friends"));
        $newDiv.load(
            LOAD_MORE_URL,
            { "start": $("#friends li").length },
            function(){
                $("#load_more_label").show();
                $("#loading_label").hide();
                if (!$newDiv.text().replace(/\s+/gi, '').length) {
                    $newDiv.remove();
                    $("#load_more_friends").remove();
                }
            });
        return false;
    }

    $("#load_more_friends").click(function(e) {
        loadMoreFriends();
    });

    function checkScroll() {
        FB.Canvas.getPageInfo(
            function(info) {
                var scrollTop = info.clientHeight + info.offsetTop + info.scrollTop;
                if (scrollTop > loadMoreButtonTop() + 100) {
                    loadMoreFriends();
                }
            });
    }

    setInterval(checkScroll, 1000);
});
