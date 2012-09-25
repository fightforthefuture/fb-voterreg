$(function() {
    function showFriendRequestDialog(friendList) {
        FB.ui(
            {
                "method": "apprequests",
                "message": "Please join me to register and pledge to vote in the upcoming election!",
                "to": friendList
            },
            friendRequestCallback);
    }

    function friendRequestCallback(response) {
        if (console) {
            console.log(response);
        }
    }

    $("#get-friends").click(function() {
        // TODO: show loading
        $.get(FRIEND_INVITE_LIST_URL,
              function(result) {
                  // TODO: hide loading
                  showFriendRequestDialog(result);
              });
        return false;
    });

    function batchesLoaded(response) {
        $(".num-registered").text(response["num_registered"]);
        $(".num-pledged").text(response["num_pledged"]);
        $(".num-friends").text(response["num_friends"]);
        var newBoxes = response["boxes"];
        for (var i = 0; i < newBoxes.length; i++) {
            $(".boxes .loadingbox").before(newBoxes[i]);
        }
        if (!response["finished"]) {
            setTimeout(loadBatches, 2000);
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
        setTimeout(loadBatches, 2000);
    }
});