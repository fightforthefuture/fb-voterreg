$(function() {
    function batchInvited(batchID) {
        // TODO: show loading animation
        var facesHTML = $("#next-to-invite .faces").html();
        $("#next-to-invite").load(
            MARK_MISSION_BATCH_INVITED,
            { "batch_id": batchID },
            function(response, status) {
                if (status != "error") {
                    $("#last-invited .faces").html(facesHTML);
                    $("#last-invited a").show();
                }
            });
    }

    function showFriendRequestDialog(fbuids, batchID) {
        if (DEBUG_APP_REQUESTS) {
            batchInvited(batchID);
            return;
        }
        FB.ui(
            {
                "method": "apprequests",
                "message": INVITE_MESSAGE,
                "to": fbuids
            },
            function(response) {
                if (response) {
                    if (response["to"] && response["to"].length > 0) {
                        batchInvited(batchID);
                    }
                }
            });
    }

    $(document).on("click", "#next-to-invite a", function(e) {
        var fbuids = [];
        $("#next-to-invite img").each(function() {
            fbuids.push($(this).data("uid"));
        });
        showFriendRequestDialog(
            fbuids.join(","),
            parseInt($(this).data("id")));
        return;
    });
});