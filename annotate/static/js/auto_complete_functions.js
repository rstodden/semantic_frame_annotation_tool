var autocompletion_frame_type = new autoComplete({
    selector: '#f-type_other_text',
    minChars: 3,
    source: function(term, suggest) {
        term = term.toLowerCase();
        var choices = eval($("input[name=all_frame_types]").val());
        var matches = [];
        for (i = 0; i < choices.length; i++) {
            if (~choices[i].toLowerCase().indexOf(term)) {
                matches.push(choices[i]);
                suggest(matches);
            }
        }
    }
});


var autocompletion_implied_frame_type = new autoComplete({
    selector: '#subordinated_frame_type_field',
    minChars: 3,
    source: function(term, suggest) {
        term = term.toLowerCase();
        var choices = eval($("input[name=all_frame_types]").val());
        var matches = [];
        for (i = 0; i < choices.length; i++) {
            if (~choices[i].toLowerCase().indexOf(term)) {
                matches.push(choices[i]);
                suggest(matches);
            }
        }
    }
});

var autocompletion_slot_type_add = new autoComplete({
    selector: "#other_core_type_add",
    minChars: 0,
    source: function(term, suggest) {
        term = term.toLowerCase();
        var choices = all_slot_types;
        var matches = [];
        for (i = 0; i < choices.length; i++) {
            if (~choices[i].toLowerCase().indexOf(term)) {
                matches.push(choices[i]);
                suggest(matches);
            }
        }
    }
});

var autocompletion_slot_type_edit = new autoComplete({
    selector: "#other_core_type_edit",
    minChars: 0,
    source: function(term, suggest) {
        term = term.toLowerCase();
        var choices = all_slot_types;
        var matches = [];
        for (i = 0; i < choices.length; i++) {
            if (~choices[i].toLowerCase().indexOf(term)) {
                matches.push(choices[i]);
                suggest(matches);
            }
        }
    }
});


/*var autocompletion_semantic_role_edit = new autoComplete({
    selector: "#role_text_edit",
    minChars: 0,
    source: function(term, suggest) {
        term = term.toLowerCase();
        var choices = all_semantic_roles;
        var matches = [];
        for (i = 0; i < choices.length; i++) {
            if (~choices[i].toLowerCase().indexOf(term)) {
                matches.push(choices[i]);
                suggest(matches);
            }
        }
    }
});


var autocompletion_semantic_role_add = new autoComplete({
    selector: "#role_text_add",
    minChars: 0,
    source: function(term, suggest) {
        term = term.toLowerCase();
        var choices = all_semantic_roles;
        var matches = [];
        for (i = 0; i < choices.length; i++) {
            if (~choices[i].toLowerCase().indexOf(term)) {
                matches.push(choices[i]);
                suggest(matches);
            }
        }
    }
});*/


var dragposition = '';
/* draggable windows*/
$("#addElements").draggable({
    handle: ".modal-header",
    drag: function(event,ui){
      dragposition = ui.position;
   }
});

$("#myModal").draggable({
    handle: ".modal-header",
    drag: function(event,ui){
      dragposition = ui.position;
   }
});

$("#skipModal").draggable({
    handle: ".modal-header",
    drag: function(event,ui){
      dragposition = ui.position;
   }
});