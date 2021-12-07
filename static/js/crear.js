$(document).ready(function(e) {
	$('#fecha').datetimepicker();

	$(document).on('submit','form',function(e) {
		e.preventDefault();
		$.ajax({
			url: "nuevacita",
			type: 'POST',
			data: $(this).serialize(),
			dataType: 'JSON',
			success: function (result) {
				if(result.error) {
					$('.alert').addClass(result.alert);
					$('.alert').html(result.message);
				} else {
					window.location = 'citas';
				}
			}

		});
	});
});