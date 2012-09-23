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
});