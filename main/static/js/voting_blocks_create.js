$(function() {
    $('#id_name').bind('keyup change', function(){
        $('#sample-name').text($('#id_name').val() == '' ? 'Voting block name' : $('#id_name').val());
    });
    $('#id_description').bind('keyup change', function(){
        $('#sample-description').text($('#id_description').val() == '' ? 'Description / share text' : $('#id_description').val());
    });
    $('#id_organization_name').bind('keyup change', function(){
        $('#sample-organization-name').text($('#id_organization_name').val() == '' ? 'Organization Name' : $('#id_organization_name').val());
    });
    $('#id_organization_website').bind('keyup change', function(){
        $('#sample-organization-website').attr('href', $('#id_organization_website').val() == '' ? '#' : $('#id_organization_website').val());
    });
    $('#id_organization_privacy_policy').bind('keyup change', function(){
        $('#sample-organization-privacy-policy').attr('href', $('#id_organization_privacy_policy').val() == '' ? '#' : $('#id_organization_privacy_policy').val());
    });
    $('input[type=file]').customFileInput();
});
