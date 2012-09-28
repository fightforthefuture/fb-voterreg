$(function() {
    function requestCallback() {
        
    }

    $(".invite-friends").click(function() {
        FB.ui(
            {
                method: 'apprequests',
                message: 'The 2012 election is almost here-- join my voting network to see which of our friends are registered to vote!'
            }, requestCallback);
        return false;
    });
});