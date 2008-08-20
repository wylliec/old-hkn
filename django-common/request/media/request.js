
states = ["unknown", "accepted", "rejected"];
states_actions = {"unknown" : false, "accepted" : true, "rejected" : undefined};
function register_request() {
    for(var i = 0; i<states.length; i++) {
        state = states[i];
        action = states_actions[state];
        $('.request_' + state).each( function() {
            $(this).click( function () {
                checkbox_changed(action, this.id.split("_")[1]);
            });
        });
    }
};

function request_select(id, state) {
    $('.request_' + id).removeClass('request_selected');
    $('#request_' + id + '_' + state).addClass('request_selected');
}


$(document).ready( register_request );
