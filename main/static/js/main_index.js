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
            $("#wont-vote-modal").modal("show")
            return false;
        });

    $(document).on(
        "click", "#records-are-wrong",
        function() {
            $("#whoops-modal").modal("show")
            return false;
        });

    $(document).on(
        "click", "#wont-vote-modal .btn",
        function() {
            // TODO: won't vote reason to database and then get me to invite friends.
            console.log("wont vote dialog button clicked");
            return false;
        });

    $(document).on(
        "click", "#whoops-modal .btn-green",
        function() {
            // TODO: save registration status to database and to votizen api and then get me to pledge.
            console.log("records are wrong");
            return false;
        });

    $(document).on(
        "click", "#whoops-modal .btn-cancel",
        function() {
            $("#whoops-modal").modal("hide");
            return false;
        });
});