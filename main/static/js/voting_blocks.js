$(function() {
    $('.note .close').click(function(){
        $(this).parent().slideUp();
        var date = new Date();
        date.setTime(date.getTime()+(50*360*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
        document.cookie = "voting_block_note=1"+expires+"; path=/";
    });
});
