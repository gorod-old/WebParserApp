$(function() {
    var spreadsheet_check = false

    $('#parser-form').on('submit', function() {
        event.preventDefault();
        run_parser();
    });

    $('input[name=spreadsheet]').on('input', function() {
        if($('input[name=spreadsheet]').val() != '') spreadsheet_check = true
    })

    $('#spreadsheet-clear-bt').on('click', function() {
        event.preventDefault();
        var text = $('input[name=spreadsheet').val();
        $('input[name=spreadsheet').val('');
        if(text != '' && !spreadsheet_check) {
            $('#parser-form-submit').html('Update Parser');
            $('#parser-form-submit').css("display", "inline-block");
        }
    })

    $('#parser-form-stop').on('click', function() {
        event.preventDefault();
        $('.load_screen').css("display", "block");
        $.ajax({
            url: 'stop-parser/',
            type: 'get',
            success: function (data) {
                console.log('response data: ', data)
                if (data['success'] == true) {
                    spreadsheet_check = false
                    $('#parser-form-stop').css("display", "none");
                    $('#parser-form-submit').css("display", "inline-block");
                    $('#parser-form-submit').html('Start Parser');
                    $('#parser-status').css("display", "none");
                    $('input[name=spreadsheet').val('');
                    $('.load_screen').css("display", "none");
                }
            }
        });
    })

    function run_parser() {
        var name = $('input[name=name]').val();
        var spreadsheet = $('input[name=spreadsheet]').val();
        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
        url = 'run-parser/';
        data = {
            'parser_name': name,
            'spreadsheet': spreadsheet,
        }
        $.ajax({
            url: url,
            type: 'post',
            headers: { 'X-CSRFToken': csrftoken },
            data: JSON.stringify(data),
            dataType: 'json',
            success: function (data) {
                console.log('response data: ', data)
                if (data['success'] == false) {
                    var html = '<p>' + data['message'] + '</p>' + data['link']
                    $('#modal-dialog-parser .modal-body').html(html);
                    $('#modal-dialog-parser').modal('show');
                } else {
                    spreadsheet_check = false
                    $('#parser-form-submit').css("display", "none");
                    $('#parser-form-stop').css("display", "inline-block");
                    $('#parser-status').css("display", "block");
                }
            }
        });
    }
});

function copyToClipboard() {
  var copyText = document.getElementById("id_app_link");

  /* Select the text field */
  copyText.select();
  copyText.setSelectionRange(0, 99999); /* For mobile devices */

  navigator.clipboard.writeText(copyText.value);
}
