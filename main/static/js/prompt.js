console.log('starting');

(function($){

    window.prompt = {};

    prompt.modal = function(type){
        var params = {};
        if(typeof type !== "undefined"){
            params['type'] = type;
        }
        console.log('modal starting');
        $.ajax({
            'url': PROMPT_URL,
            'data': params,
            'success': function(data){
                console.log('modal success');
                var $body = $('body'),
                    $container = $('#container');
                
                var $overlay = $('<div />', {
                    'id': 'modal-overlay'
                }).hide().addClass('hidden').appendTo($body);
                var $prompt = $('<div />', {
                    'class': 'prompt',
                    'html': data
                }).addClass('hidden').appendTo($body);
                var $closeBtn = $('<button />', {
                    'text': 'close',
                    'class': 'close'
                }).appendTo($prompt);

                var closeModal = function(){
                    $overlay.addClass('hidden');
                    $prompt.addClass('hidden');
                    $container.removeClass('blurred');
                    $(document).unbind('.closemodal');
                    setTimeout(function(){
                        $overlay.remove();
                        $prompt.remove();
                    }, 400);
                };

                var openModal = function(){
                    $overlay.show().removeClass('hidden');
                    $prompt.show().removeClass('hidden');
                    $container.addClass('blurred');
                    $closeBtn.bind('click.closemodal', closeModal);
                    $(document).bind('keyup.closemodal', function(e) {
                        if(e.keyCode == 27){
                            closeModal();
                        }
                    });
                };

                console.log(data);

                if(!!data){
                    setTimeout(openModal, 100);
                }

            }
        });
    };

})(jQuery);