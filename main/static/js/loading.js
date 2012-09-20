$(function() {
    $.get(
        FETCH_ME_URL,
        function(url) {
            window.location.assign(url);
        });
});
