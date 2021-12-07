$(document).ready(function(e) {
	$(document).on('click','.eliminar',function(e) {
		e.preventDefault();
		var id = $(this).attr('data-id'); //Identificador de la cita
		var params = {};
		params.idcita = id
		$.ajax({
			url: "eliminar",
			type: 'POST',
			data: params,
			dataType: 'JSON',
			success: function (result) {
				if(result.error) {
					alert(result.message);
				} else {
					location.reload();
				}
			}

		});

	});
});