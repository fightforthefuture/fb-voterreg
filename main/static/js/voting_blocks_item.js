$(function() {

    function inviteCustom(fbuid) {
        FB.ui(
            {
                method: "send",
                to: fbuid,
                name: "Vote. And help me get all our friends to vote.",
                link: window['INVITE_LINK'],
                name: window['INVITE_NAME'],
                description: window['INVITE_DESCRIPTION'],
                picture: window['INVITE_PICTURE']
            }
        );
        return false;
    }

    $('.invite-to-block').click(function(e){ inviteCustom(); });
});
