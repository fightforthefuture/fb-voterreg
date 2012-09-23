$(function() {
    var pledged = false;

    function navigateToInvite() {
        window.location.assign("/invite_friends");
    }

    $("#pledge-to-vote").click(function(e) {
        $("#pledge-modal").modal("show");
        return false;
    });

    $("#yes-will-vote").click(function(e) {
        $.getJSON(
            SUBMIT_PLEDGE_URL,
            function(response) {
                pledged = true;
                $('#pledge-modal .prepledge').hide();
                $('#pledge-modal .postpledge').fadeIn();
                setTimeout(navigateToInvite, 5 * 1000);
            });
        return false;
    });

    $("#pledge-modal").on("hidden", function() {
        if (pledged) {
            navigateToInvite();
        }
    });
});
