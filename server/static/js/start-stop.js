$(document).ready(function(){
	$('#start').click(function(){
		if(!$(this).hasClass("disabled")){
		    $.ajax({
			    url : '/start',
				type : 'GET',
				async : false,
				});
		    $('#stop').toggleClass('disabled');
		    $('#start').toggleClass('disabled');
		}
	    });

	$('#stop').click(function(){
		if(!$(this).hasClass("disabled")){
		    $.ajax({
			    url : '/stop',
				type : 'GET',
				async : false,
				});
		    $('#start').toggleClass('disabled');
		    $('#stop').toggleClass('disabled');
		}
	    }); 
});