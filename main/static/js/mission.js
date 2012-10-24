$(function() {
    function batchInvited(batchID, uninvitedNo) {
        // TODO: show loading animation
        var $justInvited = $("#uninvited-" + uninvitedNo);
        var $next = $("#uninvited-" + ((uninvitedNo + 1) % 2));
        $justInvited.find(".invite").hide();
        $justInvited.find(".invited").show();
        $.getJSON(
            MARK_MISSION_BATCH_INVITED,
            { "batch_id": batchID },
            function(result) {
                $(window).trigger('checkNotifications');
                // TODO: hide loading animation
                if ($next.find(".invited:visible").length > 0) {
                    $next.html(result["html"]);
                }
                fillInInvitedBadges(result["num_invited"], result["num_friends"]);
            });
    }

    function fillInInvitedBadges(numInvited, numFriends) {
        $("#num-invited").text(numInvited + "");
        $(".invited-badges .badge").each(function() {
            var cutoff = $(this).data("cutoff");
            if (cutoff != -1 && cutoff < numInvited) {
                $(this).addClass("badge-accomplished");
            }
            else if (cutoff == -1 && numInvited >= numFriends) {
                $(this).addClass("badge-accomplished");
            }
        });
    }

    function showFriendRequestDialog(fbuids, batchID, uninvitedNo) {
        if (DEBUG_APP_REQUESTS) {
            batchInvited(batchID, uninvitedNo);
            return;
        }
        FB.ui(
            {
                "message": "The 2012 election is almost here -- are you going to vote?  This app gets you everything you need, and helps you recruit your friends.",
                "method": "apprequests",
                "to": fbuids
            },
            function(response) {
                if (response) {
                    if (response["to"] && response["to"].length > 0) {
                        batchInvited(batchID, uninvitedNo);
                    }
                }
            });
    }

    $(document).on("click", ".mission-box-mass a.invite", function(e) {
        var fbuids = [];
        var $uninvited = $(this).parents(".uninvited");
        $uninvited.find("img").each(function() {
            fbuids.push($(this).data("uid"));
        });
        showFriendRequestDialog(
            fbuids.join(","),
            parseInt($(this).data("id")),
            parseInt($uninvited.data("id")));
        return;
    });
});
