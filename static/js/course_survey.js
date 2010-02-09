
states = ["enabled", "disabled"];
states_actions = {"disabled" : false, "enabled" : true};
function register_options() {
    for(var i = 0; i<states.length; i++) {
        state = states[i];
        action = states_actions[state];
        $('.survey_' + state).each( function() {
            $(this).click( function () {
                action = states_actions[this.id.split("_")[2]];
                checkbox_changed(action, this.id.split("_")[1]);
            });
        });
    }
};

function option_select(id, state) {
    $('.klass_' + id).removeClass('option_selected');
    $('#klass_' + id + '_' + state).addClass('option_selected');
};

function checkbox_changed(state, value){
  //var identifier = $("#ajaxwrapper").attr("identifier");
  var identifier = "course_survey"

  if (state == true) {
    action = "add";
  } else {
    action = "remove";
  }

  $.ajax({
    url: ajaxlist_checkbox_post_address,
    type: "POST",
    data: {"action": action, "identifier": identifier, "value": value},
    dataType: "script",
    });
}


//$(document).ready( register_request );
