$(function() {
    function loadFriends() {
        $.getJSON(
            FETCH_FRIENDS_URL,
            function(response) {
                if (response["fetched"]) {
                    $("#main-friends").html(response["html"]);
                }
                else {
                    setTimeout(loadFriends, 1000);
                }
            });
    }
    if (LOAD_FRIENDS) {
        loadFriends();
    }
});
