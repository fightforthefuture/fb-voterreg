$(function() {
    $("#pledge").click(function(e) {
        var explicit_share = !!$('[name="tell-friends"]:checked').length;
        $.getJSON(
            SUBMIT_PLEDGE_URL + '?explicit_share=' + explicit_share,
            function(response) {
                window.location.assign(response["next"]);
            });
        return false;
    });
});
