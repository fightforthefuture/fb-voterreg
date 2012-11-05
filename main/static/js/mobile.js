app.showPanel = function(panelName){
    var $panel = $('#' + panelName);
    $panel.siblings().hide();
    $panel.show();
};
app.error = function(){ app.showPanel('error'); };
app.loading = function(){ app.showPanel('loading'); };
app.pledgeForm = function(){ app.showPanel('pre-pledge'); };
app.isPledged = function(){ app.showPanel('post-pledge'); };


window.fbAsyncInit = function() {
    FB.init({
        appId: app.APP_ID,
        status: true,
        cookie: true,
        xfbml: true,
        oauth: true
    });
    FB.Event.subscribe('auth.authResponseChange', function(response) {
        if(response.authResponse){
            app.userID = response.authResponse.userID;
            $(document).trigger('facebook-login');
        }else{
            app.error();
            console.log('Error logging the user in:');
            console.log(response);
        }
    });
};


app.pledgeButton = (function(){
    var $buttons = $('#pledge-btn');
    $buttons.click(function(evt){
        $(document).trigger('pledge');
    });
    return $buttons;
})();


app.shareButtons = (function(){
    var $shareButtons = $('.btn-share');
    $shareButtons.live('click', function(evt){
        $(document).trigger('share');
    });
    return $shareButtons;
})();


// When the user is successfully authenticated against Facebook
$(document).bind('facebook-login', function(){
    FB.api(app.PLEDGE_ACTION_URL, 'get', {
        'vote_obj': app.VOTE_OBJ_URL
    }, function(response) {
        if (!response || response.error) {
            app.error();
        } else {
            var num_pledges = response.data.length;
            if(num_pledges > 0){
                app.isPledged();
            }else{
                app.pledgeForm();
            }
        }
    });
});


// When the user pledges to vote
$(document).bind('pledge', function(){
    app.loading();
    FB.api(app.PLEDGE_ACTION_URL, 'post', {
        'vote_obj': app.VOTE_OBJ_URL,
        'fb:explicitly_shared': $('#explicit').is(':checked') ? 'true' : 'false'
    }, function(response) {
        if (!response || response.error) {
            app.error();
        } else {
            app.isPledged();
        }
    });
});

$(document).bind('share', function(){
    console.log('share');
    FB.ui({
        'method': 'feed',
        'name': 'Vote With Friends',
        'link': app.APP_SHARE_URL,
        'picture': 'http://fbrell.com/f8.jpg',
        'caption': 'Reference Documentation',
        'description': 'Dialogs provide a simple, consistent interface for applications to interface with users.'
    }, function(response) {
        if (response && response.post_id) {
          alert('Post was published.');
        } else {
          alert('Post was not published.');
        }
    });
});
