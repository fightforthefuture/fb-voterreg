$(function() {
    $("#pledge").click(function(e) {
        $.getJSON(
            SUBMIT_PLEDGE_URL,
            function(response) {
                window.location.assign(response["next"]);
            });
        return false;
    });
});
