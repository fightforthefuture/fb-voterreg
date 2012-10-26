$(function() {
    $('.note .close').click(function(){
        $(this).parent().slideUp();
        var date = new Date();
        date.setTime(date.getTime()+(50*360*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
        document.cookie = "voting_block_note=1"+expires+"; path=/";
    });

    var request = 0;
    function search(filter, text) {
        if ($(".search-loading").is(":visible")) {
            return
        }
        $(".search-loading")
            .css('width', $('.search').width() + 'px')
            .css('height', $('.search').height() + 'px')
            .fadeIn();
        $.get(
            SEARCH_URL,
            {
                "skip": 0,
                "text": text,
                "filter": filter
            },
            function(response){
                $(".search-loading").fadeOut();
                $('.search-results').html(response);
                bind();
            });
        return false;
    };

    function loadMore(e) {
        if ($("#load_more_voting_blocks_loading").is(":visible")) {
            return
        }
        $("#load_more_voting_blocks_label").hide();
        $("#load_more_voting_blocks_loading").show();
        $.get(
            SEARCH_URL,
            {
                "skip": $("ul.search-list li").length,
                "text": $("div.search-input input").val(),
                "filter": $('ul.search-filters li.active').data('filter')
            },
            function(response){
                $("#load_more_voting_blocks_label").show();
                $("#load_more_voting_blocks_loading").hide();
                if (!response.replace(/\s+/gi, '').length) {
                    $("#load_more_voting_blocks").remove();
                } else {
                    $("ul.search-list").append($(response));
                }
            });
        return false;
    }

    function bind() {
        $("div.search-input input").keyup(function(e) {
            if (e.which == 13) {
                search($('ul.search-filters li.active').data('filter'), $("div.search-input input").val());
            }
        });
        $("div.search-input .clear").click(function(e) {
            $("div.search-input input").val('');
            search($('ul.search-filters li.active').data('filter'), $("div.search-input input").val());
        });
        $("ul.search-filters li span").click(function(e) {
            search($(e.target).parent().data('filter'), $("div.search-input input").val());
        });
        $("#load_more_voting_blocks").click(function(e) { loadMore(e); });
    }

    bind();

    function checkScroll() {
        FB.Canvas.getPageInfo(function(info) {
            if ($("#load_more_voting_blocks").length == 0) return;
            var buttonTop = $("#load_more_voting_blocks").offset().top - $(document).scrollTop();
            var scrollTop = info.clientHeight + info.offsetTop + info.scrollTop;
            if (scrollTop > buttonTop + 100) {
                loadMore();
            }
        });
    }

    setInterval(checkScroll, 1000);
});
