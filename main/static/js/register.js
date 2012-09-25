$(function() {
    $("#not-eligible").click(
        function() {
            if (confirm("Are you sure you're not eligible?")) {
                $.getJSON(WONT_VOTE_URL,
                          function(result) {
                              window.location.assign(result["next"]);
                          });
            }
            return false;
        });

    $("#already-registered").click(
        function() {
            if (confirm("Are you sure you're already registered?")) {
                $.getJSON(ACTUALLY_REGISTERED_URL,
                          function(result) {
                              window.location.assign(result["next"]);
                          });
            }
            return false;
        });
});