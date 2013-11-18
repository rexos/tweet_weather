$(function() {

    var WEB_SOCKET_SWF_LOCATION = '/static/js/socketio/WebSocketMain.swf',
        socket = io.connect('/new_posts');

    socket.on('new_post', function(score, weather, description, latitude, longitude, correlation) {
    var weightedLoc = {
      location: new google.maps.LatLng(latitude, longitude),
      weight: correlation*10
    };
    pointArray.push(weightedLoc);
    });

});
