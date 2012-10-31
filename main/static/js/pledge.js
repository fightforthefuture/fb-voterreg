$(function() {
    $("#pledge").click(function(e) {
        var explicit_share = !!$('[name="tell-friends"]:checked').length,
            join_block = AUTOJOIN || !!$('[name="join-block"]:checked').length,
            url = SUBMIT_PLEDGE_URL + '?explicit_share=' + explicit_share + '&join_block=' + join_block;
        $.getJSON(
            url,
            function(response) {
                window.location.assign(response["next"]);
            });
        return false;
    });
});
