$(function() {
    console.log("running");
    $("#i-wont-vote").click(
        function() {
            console.log("clicked");
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