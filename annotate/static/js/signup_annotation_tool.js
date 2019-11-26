$('#password_1, #password_2').on('keyup', function () {
  if ($('#password_1').val() == $('password_2').val()) {
    $('#message').html('Matching').css('color', 'green');
  } else
    $('#message').html('Not Matching').css('color', 'red');
});