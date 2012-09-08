$(function() {
    function loadFriends() {
        // TODO: show thing for loading friends.
        $(".friends-content").load(
            FETCH_FRIENDS_URL,
            function() {
                // TODO: hide thing for loading friends.
            });
    }

    if (LOAD) {
        $("#main-content").load(
            FETCH_ME_URL,
            function() {
                $("#loading").hide();
                loadFriends();
            });
    }
    else if (LOAD_FRIENDS) {
        loadFriends();
    }
});