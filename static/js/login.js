$(document).ready(function(e) {
	$(document).on('submit','form#login',function(e) {
		e.preventDefault();
		$.ajax({
			url: "loginuser",
			type: 'POST',
			data: $(this).serialize(),
			dataType: 'JSON',
			success: function (result) {
				if(result.error) {
					$('#login .alert').addClass(result.alert);
					$('#login .alert').html(result.message);
					$('#login #'+result.focus).focus();
				} else {
					window.location = 'citas';
				}
			}

		});
	});

	$(document).on('submit','form#register',function(e) {
		e.preventDefault();
		var id = $(this).attr('id'); //FORM ID
		$.ajax({
			url: "register",
			type: 'POST',
			data: $(this).serialize(),
			dataType: 'JSON',
			success: function (result) {
				$('#register .alert').addClass(result.alert);
				$('#register .alert').html(result.message);

				if(result.error) {
					$('#register #'+result.focus).focus();
				} else {
					$('#register').trigger('reset');
				}
			}

		});

	});
});