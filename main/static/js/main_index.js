$(function() {
    function loadFriends() {
        $("#loading-friends").show();
        $.getJSON(
            FETCH_FRIENDS_URL,
            function(response) {
                if (response["fetched"]) {
                    $("#loading-friends").hide();
                    $("#main-friends").html(response["html"]);
                }
                else {
                    setTimeout(loadFriends, 500);
                }
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

    $(document).on(
        "click", "#i-wont-vote",
        function() {
            
            return false;
        });

    $(document).on(
        "click", "#records-are-wrong",
        function() {
            
            return false;
        });
});