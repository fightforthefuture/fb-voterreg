$(function() {
    function batchInvited(batchID, uninvitedNo) {
        // TODO: show loading animation
	var $justInvited = $("#uninvited-" + uninvitedNo);
	var $next = $("#uninvited-" + ((uninvitedNo + 1) % 2));
	$justInvited.find(".invite").hide();
	$justInvited.find(".invited").show();
	$.get(MARK_MISSION_BATCH_INVITED,
	      { "batch_id": batchID },
	      function(result) {
		  // TODO: hide loading animation
		  if ($next.find(".invited:visible").length > 0) {
		      $next.html(result);
		  }
	      });
    }

    function showFriendRequestDialog(fbuids, batchID, uninvitedNo) {
        if (DEBUG_APP_REQUESTS) {
            batchInvited(batchID, uninvitedNo);
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
                        batchInvited(batchID, uninvitedNo);
                    }
                }
            });
    }

    $(document).on("click", ".mass-invites a.invite", function(e) {
        var fbuids = [];
	var $uninvited = $(this).parents(".uninvited");
	$uninvited.find("img").each(function() {
            fbuids.push($(this).data("uid"));
	});
        showFriendRequestDialog(
            fbuids.join(","),
            parseInt($(this).data("id")),
	    parseInt($uninvited.data("id")));
        return;
    });
});