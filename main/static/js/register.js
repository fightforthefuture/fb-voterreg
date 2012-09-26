$(function() {
    $("#not-eligible").click(
        function() {
            $.getJSON(
                WONT_VOTE_URL,
                function(result) {
                    window.location.assign(result["next"]);
                });
            return false;
        });

    $("#already-registered").click(
        function() {
            $.getJSON(
                ACTUALLY_REGISTERED_URL,
                function(result) {
                    window.location.assign(result["next"]);
                });
            return false;
        });
});