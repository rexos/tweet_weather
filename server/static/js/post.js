$(function() {

    var WEB_SOCKET_SWF_LOCATION = '/static/js/socketio/WebSocketMain.swf',
        socket = io.connect('/new_posts');

    socket.on('new_post', function(score, weather, description) {
	var id = 1;
	if($('td:first').text()){
	    var id = parseInt($('td:first').text(),10) + 1;
	}
    	$("#header-line").last().after("<tr><td>"+id+"</td><td>"+score+"</td><td>"+weather+"</td><td>"+description+"</td></tr>");
    });


});
