$(function() {
    var UPDATE_INTERVAL = 5000;

    var InviteMessages = {
        1: "I'm sending this to all my friends who were too young to vote in '08, but are old enough now.  Click here to register and pledge to vote!",
        2: "I'm sending this to all my friends who moved out of state.  Use this to make sure you're registered and pledged to vote this year!",
        4: "The 2012 election is almost here -- join my voting netowrk to see which of our friends are registered to vote!",
        5: "The 2012 election is almost here -- join my voting netowrk to see which of our friends are registered to vote!"
    };

    function showFriendRequestDialog(friendList, batchID, batchType) {
        _gaq.push(["_trackPageview", "/show_batch_invite"]);
        var message = null;
        if (batchType == 3) {
            message = "I'm sending this to all my friends in " + MY_CITY + 
                " who aren't registered to vote yet. It's really " +
                "important that you guys register and promise to vote.";
        }
        else {
            message = InviteMessages[batchType];
        }
        FB.ui(
            {
                "method": "apprequests",
                "message": message,
                "to": friendList
            },
            function(response) {
                if (response) {
                    _gaq.push(["_trackPageview", "/batch_invited"]);
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