$(function() {
    var UPDATE_INTERVAL = 5000;

    function showFriendRequestDialog(friendList, batchID, batchType) {
        if (DEBUG_APP_REQUESTS) {
            friendsInvited(batchID);
            return;
        }
        _gaq.push(["_trackPageview", "/show_batch_invite"]);
        _kmq.push(["record", "Opened batch invite dialog"]);
        FB.ui(
            {
                "message": "The 2012 election is almost here -- are you going to vote?  This app gets you everything you need, and helps you recruit your friends.",
                "method": "apprequests",
                "to": friendList
            },
            function(response) {
                if (response) {
                    _gaq.push(["_trackPageview", "/batch_invited"]);
                    _kmq.push(["record", "Invited a batch"]);
                    friendsInvited(batchID);
                }
            });
    }

    function friendsInvited(batchID) {
        $.getJSON(
            MARK_BATCH_INVITED_URL,
            { "batch_id": batchID },
            function(result) {
                $('[data-batch-id="' + batchID + '"]').slideUp();
                $(window).trigger('checkNotifications');
            });
    }

    $(document).on("click", ".friend-box a", function() {
        var fbuids = [];
        var friendBox = $(this).parents(".friend-box");
        friendBox.find(".friends img").each(function() {
            fbuids.push($(this).data("uid"));
        });
        showFriendRequestDialog(
            fbuids.join(","), 
            parseInt(friendBox.data("batch-id")),
            parseInt(friendBox.data("batch-type")));
        return false;
    });

    function batchesLoaded(response) {
        var numProcessed = response["num_processed"];
        var numFriends = response["num_friends"];
        $(".num-registered").text(response["num_registered"]);
        $(".num-pledged").text(response["num_pledged"]);
        $(".num-friends").text(numFriends);
        var percentDone = Math.min(100, Math.max(0, Math.floor(100.0 * numProcessed / numFriends)));
        $(".progress-bar span").css("width", percentDone + "%");
        var newBoxes = response["boxes"];
        for (var i = 0; i < newBoxes.length; i++) {
            $(".boxes .loadingbox").before(newBoxes[i]);
        }
        if (!response["finished"]) {
            setTimeout(loadBatches, UPDATE_INTERVAL);
        }
        else {
            $(".boxes .loadingBox").remove();
        }
    }

    function loadBatches() {
        var existingBatchIds = [];
        $(".friend-box").each(function() {
            existingBatchIds.push($(this).data("batch-id"));
        });
        $.getJSON(
            FETCH_UPDATED_BATCHES_URL,
            { "batchids": existingBatchIds.join(",") },
            batchesLoaded);
    }

    if (stillLoading) {
        setTimeout(loadBatches, UPDATE_INTERVAL);
    }
});
