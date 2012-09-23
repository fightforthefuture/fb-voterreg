$(function() {
    console.log("running");
    $("#i-wont-vote").click(
        function() {
            $("#wont-vote-modal").modal("show")
            return false;
        });

    $("#records-are-wrong").click(
        function() {
            $("#whoops-modal").modal("show")
            return false;
        });

    $(document).on(
        "click", "#whoops-modal .btn-green",
        function() {
            $.getJSON(
                ACTUALLY_REGISTERED_URL,
                function(response) {
                    window.location.assign(response["next"]);
                });
            return false;
        });

    $(document).on(
        "click", "#whoops-modal .btn-cancel",
        function() {
            $("#whoops-modal").modal("hide");
            return false;
        });

});