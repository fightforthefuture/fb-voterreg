$(function() {
    var UPDATE_INTERVAL = 5000;

    var InviteMessages = {
        1: "I'm sending this to all my friends who have turned 18 since the last presidential election. It's really important that you guys register and promise to vote.",
        2: "I'm sending this to all my friends who have moved out of state. It's really important that you guys register and promise to vote.",
        4: "The 2012 election is almost here -- join my voting netowrk to see which of our friends are registered to vote!",
        5: "The 2012 election is almost here -- join my voting netowrk to see which of our friends are registered to vote!"
    };

    function showFriendRequestDialog(friendList, batchID, batchType) {
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