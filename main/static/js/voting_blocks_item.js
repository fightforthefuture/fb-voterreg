$(function() {

    function invite(fbuid, callback) {
        if (DEBUG_APP_REQUESTS) {
            callback(fbuid);
            return;
        }
        FB.ui(
            {
                method: "send",
                to: fbuid,
                name: "Vote. And help me get all our friends to vote.",
                link: window['INVITE_LINK'],
                name: window['INVITE_NAME'],
                description: window['INVITE_DESCRIPTION'],
                picture: window['INVITE_PICTURE']
            }, function(response) {
                if (response && response["to"] && response["to"].length > 0 && callback) {
                    callback(fbuid);
                }
            }
        );
    }

    function batchInvited(fbuid) {
        var uninvited = $("#uninvited");
        uninvited.find(".invite").hide();
        uninvited.find(".invited").show();
        $.getJSON(
            MARK_BATCH_URL,
            { "fbuid": fbuid },
            function(result) {
                $(window).trigger('checkNotifications');
                uninvited.html(result["friends_batch_html"]);
                if(result['num_friends'] > result['num_invited']) {
                    uninvited.find(".invite").show();
                    uninvited.find(".invited").hide();
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

    $(".mission-box-mass a.invite").click(function(e) {
        var fbuids = [];
        var $uninvited = $(this).parents(".uninvited");
        $uninvited.find("img").each(function() {
            fbuids.push($(this).data("uid"));
        });
        var that = this;
        invite(
            fbuids.join(","),
            batchInvited
        );
        return;
    });

    $('#invite-custom').click(function(e){ invite(); });

});