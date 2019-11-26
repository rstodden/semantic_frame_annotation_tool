function change_hidden_elements(list_ids, type) {
    if (type === "remove") {
        for (var element_id in list_ids) {
            document.getElementById(element_id).classList.remove("hidden_element");
        }
    }
    else {
        for (var element_id in list_ids) {
            document.getElementById(element_id).classList.add("hidden_element");
        }
    }

}

window.onload = function () {
    hide_elements();
    change_color_token();
};

function go_back(element) {
    var annotation_state = $("#annotation_state").val();
    //var frame_id = document.getElementById("frame_number").value;
    //console.log("as",annotation_state)
    if (annotation_state=== "2" && ($("input[name=f-type]:checked").val() === undefined || ($("input[name=f-type]:checked").val() === "other" && $("input[name=f-type_other_text]").val() === "")))    {
        swal('Frame type missing', 'Please choose a frame type.', "warning");
    }
    else if ($("#add_custom_frame_types").val()==="False" && ($("input[name=f-type]:checked").val() === "other"  && (!$("#all_frame_types").val().slice(1,-1).split("'").includes($("input[name=f-type_other_text]").val()) || ($("input[name=f-type_other_text]").val() === ", ") || ($("input[name=f-type_other_text]").val() !== '')))) {
        swal("Wrong frame type", "Please change the frame type, currently it matches none of the listed frame types.", "warning")
    }
    else {
        element.disabled = true;
        document.getElementById("next_button").disabled = true;
        if (element.id === "back_button_save") {
            document.getElementById("save_button").disabled = true;
        }
        $.ajax({
            url: "frame",
            method: "POST",
            cache: false,
            data: {
                //f_type: frame_type_name,
                //frame_number: frame_id,
                change_type: "go_back",
                annotation_state: annotation_state,
                csrfmiddlewaretoken: jQuery("[name=csrfmiddlewaretoken]").val(),
                dataType: 'json'
            },
            success: function (data) {
                // data entspricht rueckgabewert aus backend views
                if (typeof data.error !== 'undefined') {
                    // ausfuehren wenn in data kein ergebnis zur suchanfrage gefunden
                    swal('something went wrong', data["error"], "error");
                }
                else {
                    annotation_state = data.annotation_state;
                    //console.log(annotation_state);
                    document.getElementById("annotation_state").value = data.annotation_state;
                    var frame_verb = $("#frame_verb");
                    if (annotation_state === 0) {
                        // read sentence
                        hide_elements();
                    }
                    else if (annotation_state === 1) {
                        var button_frame_type = $("#f-type_other");
                        if (button_frame_type.is(":checked")) {
                            var frame_type_text = $("#f-type_other_text").val();
                            save_frame_type(frame_type_text, other = true)
                        }

                        hide_elements();
                        frame_verb.attr('onClick', "set_selection_of_core_element_types('" + frame_verb.data('token_id') + "', '" + frame_verb.data('word_form') + "', '" + frame_verb.data('lemma') + "', '" + frame_verb.data('position') + "')");
                        // enable slider

                        $("#slider_mwc").prop("checked", true);
                        change_color_token();
                        //document.getElementById("instruction_core").classList.add("hidden_element");

                    }
                    else if (annotation_state === 2) {
                        hide_elements();
                        frame_verb.attr('onClick', "");
                        change_color_token();

                    }
                    else if (annotation_state === 3) {
                        hide_elements();
                        change_color_token();
                    }
                    else {
                        hide_elements();
                        change_color_token();
                    }
                    change_color_token();
                    element.disabled = false;
                    document.getElementById("next_button").disabled = false;
                    if (element.id === "back_button_save") {
                        document.getElementById("save_button").disabled = false;
                    }
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
                /*swal("Error: " + errorThrown
                    + "\nStatus: " + textStatus
                    + "\njqXHR: " + JSON.stringify(jqXHR)
                );*/
                swal("Error. Please contact the system operator.");
                element.disabled = false;
                document.getElementById("next_button").disabled = false;
                if (element.id === "back_button_save") {
                    document.getElementById("save_button").disabled = false;
                }
            },
            complete: function (jqXHR, textStatus) {
            }
        });
    }
}

function go_forward(element) {
    var annotation_state = $("#annotation_state").val();
    //var frame_id = document.getElementById("frame_number").value;
    //console.log($("input[name=f-type]:checked").val(), $("input[name=f-type_other_text]").val() === "", annotation_state);
    if (annotation_state=== "2" && ($("input[name=f-type]:checked").val() === undefined || ($("input[name=f-type]:checked").val() === "other" && $("input[name=f-type_other_text]").val() === "")))    {
        swal('Frame type missing', 'Please choose a frame type.', "warning");
    }
    else if ($("#add_custom_frame_types").val()==="False" && ($("input[name=f-type]:checked").val() === "other"  && (!$("#all_frame_types").val().slice(1,-1).split("'").includes($("input[name=f-type_other_text]").val()) || ($("input[name=f-type_other_text]").val() === ", ") || ($("input[name=f-type_other_text]").val() !== '')))) {
        swal("Wrong frame type", "Please change the frame type, currently it matches none of the listed frame types.", "warning")
    }
    else {
        element.disabled = true;
        if ($("input[name=f-type]:checked").val() === "other") {
            var frame_type = $("input[id=f-type_other_text]").val();
        }
        else {
            var frame_type = $("input[name=f-type]:checked").val();
        }
        document.getElementById("back_button").disabled = true;
        $.ajax({
            url: "frame",
            method: "POST",
            cache: false,
            data: {
                //f_type: frame_type_name,
                //frame_number: frame_id,
                change_type: "go_forward",
                f_type: frame_type,
                annotation_state: annotation_state,
                csrfmiddlewaretoken: jQuery("[name=csrfmiddlewaretoken]").val(),
                dataType: 'json'
            },
            success: function (data) {
                // data entspricht rueckgabewert aus backend views
                if (typeof data.error !== 'undefined') {
                    swal('something went wrong', data["error"], "error");
                    element.disabled = false;
                    document.getElementById("back_button").disabled = false;
                }
                else {
                    annotation_state = data.annotation_state;
                    console.log(annotation_state);
                    document.getElementById("annotation_state").value = annotation_state;
                    if (annotation_state === 1) {
                        var frame_verb = $("#frame_verb");
                        frame_verb.attr('onClick', "set_selection_of_core_element_types('" + frame_verb.data('token_id') + "', '" + frame_verb.data('word_form') + "', '" + frame_verb.data('lemma') + "', '" + frame_verb.data('position') + "')");
                        hide_elements();
                        change_color_token();

                    }
                    else if (annotation_state === 2) {

                        /*var button_frame_type = $("#f-type_other");
                        if (button_frame_type.is(":checked")) {
                            var frame_type_text = $("#f-type_other_text").val();
                            save_frame_type(frame_type_text,other=true)
                        }*/
                        hide_elements();
                        change_color_token();
                        //document.getElementById("instruction_sentence").classList.add("hidden_element");
                    }
                    else if (annotation_state === 3) {
                        var button_frame_type = $("#f-type_other");
                        if (button_frame_type.is(":checked")) {
                            var frame_type_text = $("#f-type_other_text").val();
                            save_frame_type(frame_type_text, other = true)
                        }
                        //enable_core_elements();
                        var mwc = $("span[class*=multiword_component]");
                        mwc.removeClass("multiword_component");
                        hide_elements();
                        $("#slider_core_element").prop("checked", true);
                        $("#slider_mwc").prop("checked", true);
                        change_color_token();
                    }
                    else if (annotation_state === 4) {
                        hide_elements();
                        change_color_token();

                    }
                    element.disabled = false;
                    document.getElementById("back_button").disabled = false;
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
                /*swal("Error: " + errorThrown
                    + "\nStatus: " + textStatus
                    + "\njqXHR: " + JSON.stringify(jqXHR)
                );*/
                swal("Error. Please contact the system operator.");
                element.disabled = false;
                document.getElementById("back_button").disabled = false;
            },
            complete: function (jqXHR, textStatus) {
            }
        });
    }
}


function change_data_target(new_target, value, data_field, clickable) {
    var elements = $("span["+data_field+"="+value+"]");
    elements.attr("data-target", new_target);
    if (clickable) {
        elements.css("cursor","pointer");
    }
    else {
        elements.css("cursor","auto");
    }
}

function enable_core_elements() {
    //change_data_target("#addElements", "token", "data-annotation", true);
    //change_data_target("#addElements", "multiword_component", "data-annotation", true);
    change_data_target("#myModal", "core_element", "data-annotation", true);
}

function disable_core_elements() {
    //change_data_target("#mwe", "token", "data-type");
    //change_data_target("#mwe", "child", "data-type");
    change_data_target(null, "token", "data-annotation");
    change_data_target(null, "core_element", "data-annotation");
    //change_data_target(null, "multiword_component", "data-annotation", true);
}

function change_annotation(new_annotation_state) {
    $("#annotation_state").val(new_annotation_state);
    hide_elements();
    change_color_token();

}

function hide_elements() {
    var annotation_state = parseInt(document.getElementById("annotation_state").value);
    //console.log(annotation_state, typeof(annotation_state));
    if (annotation_state === 0) {
        // read sentence
        $("#slider_mwc").prop("checked", false);
        $("#slider_core_element").prop("checked", false);
        disable_core_elements();
        document.getElementById("short_instruction").innerText = "1) Read the sentence";
        //document.getElementById("instruction_sentence").classList.remove("hidden_element");
        document.getElementById("frame_type_selection").classList.add("hidden_element");
        document.getElementById("back_button").classList.add("hidden_element");
        document.getElementById("mwe_block").classList.add("hidden_element");
        //document.getElementById("instruction_mwe").classList.add("hidden_element");
        //document.getElementById("instruction_core").classList.add("hidden_element");
        document.getElementById("certainty").classList.add("hidden_element");
        document.getElementById("comment_area").classList.add("hidden_element");
        document.getElementById("save_area").classList.add("hidden_element");
        document.getElementById("next_area").classList.remove("hidden_element");
        document.getElementById("slider_higlight_area").classList.remove("hidden_element");
        $('#slider_child').prop('disabled', true);
        $('#slider_mwc').prop('disabled', true);
        $('#slider_core_element').prop('disabled', true);
        document.getElementById("skip_button").classList.remove("hidden_element");
        document.getElementById("skip_reason").classList.remove("hidden_element");
        document.getElementById("current_frame_state").classList.add("hidden_element");
        document.getElementById("summary").classList.add("hidden_element");


        //change_hidden_elements(["frame_type_selection", "back_button", "mwe_block", "certainty", "comment_area", "save_area"], "add");
        //change_hidden_elements(["next_area"], "remove");
    }
    else if (annotation_state === 1) {
        // mwe annotatoin
        disable_core_elements();
        $("#slider_mwc").prop("checked", true);
        $("[name=mwe_delete]").removeClass("hidden_element");
        $("[name=mwe_edit]").removeClass("hidden_element");

        $('#slider_child').prop('disabled', false);
        $('#slider_mwc').prop('disabled', false);
        $('#slider_core_element').prop('disabled', false);

        document.getElementById("short_instruction").innerText = "2) Please mark VMWE and MWUs (if there are any).";
        //document.getElementById("instruction_sentence").classList.add("hidden_element");
        document.getElementById("frame_type_selection").classList.add("hidden_element");
        document.getElementById("back_button").classList.remove("hidden_element");
        document.getElementById("mwe_block").classList.remove("hidden_element");
        //document.getElementById("instruction_mwe").classList.remove("hidden_element");
        //document.getElementById("instruction_core").classList.add("hidden_element");
        document.getElementById("certainty").classList.add("hidden_element");
        document.getElementById("skip_button").classList.add("hidden_element");
        document.getElementById("skip_reason").classList.add("hidden_element");
        document.getElementById("comment_area").classList.add("hidden_element");
        document.getElementById("save_area").classList.add("hidden_element");
        document.getElementById("next_area").classList.remove("hidden_element");
        document.getElementById("slider_higlight_area").classList.remove("hidden_element");
        document.getElementById("current_frame_state").classList.add("hidden_element");
        document.getElementById("summary").classList.add("hidden_element");
        var frame_verb = $("#frame_verb");
        frame_verb.attr('onClick', "set_selection_of_core_element_types('"+frame_verb.attr("data-token_id")+"', '"+frame_verb.attr("data-word_form")+"', '"+frame_verb.attr("data-lemma")+"', '"+frame_verb.attr("data-position")+"')");
        var vmwes = $("span[data-verbal_mwe=1]").each(function (i, obj) {
            $(this).attr('onClick', "set_selection_of_core_element_types('"+$(this).attr("data-token_id")+"', '"+$(this).attr("data-word_form")+"', '"+$(this).attr("data-lemma")+"', '"+$(this).attr("data-position")+"')");
        })

    }
    else if (annotation_state === 2) {
        // frametype annotation
        $('#slider_child').prop('disabled', false);
        $('#slider_mwc').prop('disabled', false);
        $('#slider_core_element').prop('disabled', false);
        document.getElementById("short_instruction").innerText = "3) Annotate the frame type";
        disable_core_elements();
        //document.getElementById("instruction_sentence").classList.add("hidden_element");
        document.getElementById("frame_type_selection").classList.remove("hidden_element");
        document.getElementById("back_button").classList.remove("hidden_element");
        document.getElementById("mwe_block").classList.add("hidden_element");
        //document.getElementById("instruction_mwe").classList.add("hidden_element");
        //document.getElementById("instruction_core").classList.add("hidden_element");
        document.getElementById("certainty").classList.add("hidden_element");
        document.getElementById("comment_area").classList.add("hidden_element");
        document.getElementById("save_area").classList.add("hidden_element");
        document.getElementById("skip_button").classList.add("hidden_element");
        document.getElementById("skip_reason").classList.add("hidden_element");
        document.getElementById("next_area").classList.remove("hidden_element");
        document.getElementById("slider_higlight_area").classList.remove("hidden_element");
        document.getElementById("current_frame_state").classList.remove("hidden_element");
        document.getElementById("summary").classList.add("hidden_element");
    }
    else if (annotation_state === 3) {
        // core element annotation
        //enable_core_elements();
        $('#slider_child').prop('disabled', false);
        $('#slider_mwc').prop('disabled', false);
        $('#slider_core_element').prop('disabled', false);
        $("#slider_mwc").prop("checked", true);
        $("#slider_core_element").prop("checked", true);
        document.getElementById("short_instruction").innerText = "4) Add core elements";
        //document.getElementById("instruction_sentence").classList.add("hidden_element");
        document.getElementById("frame_type_selection").classList.add("hidden_element");
        document.getElementById("back_button").classList.remove("hidden_element");
        document.getElementById("mwe_block").classList.remove("hidden_element");
        //document.getElementById("instruction_mwe").classList.add("hidden_element");
        //document.getElementById("instruction_core").classList.remove("hidden_element");
        document.getElementById("certainty").classList.add("hidden_element");
        document.getElementById("comment_area").classList.add("hidden_element");
        document.getElementById("save_area").classList.add("hidden_element");
        document.getElementById("next_area").classList.remove("hidden_element");
        document.getElementById("skip_button").classList.add("hidden_element");
        document.getElementById("skip_reason").classList.add("hidden_element");
        document.getElementById("slider_higlight_area").classList.remove("hidden_element");
        document.getElementById("current_frame_state").classList.remove("hidden_element");
        document.getElementById("summary").classList.add("hidden_element");

        document.getElementById("sentence_presentation").classList.remove("hidden_element");
        $("[name=mwe_delete]").addClass("hidden_element");
        $("[name=mwe_edit]").addClass("hidden_element");
        //document.getElementsByName("mwe_delete").classList.add("hidden_element");
        //document.getElementsByName("mwe_edit").classList.add("hidden_element");
        var frame_verb = $("#frame_verb");
        frame_verb.attr('onClick', "");
        $("span[data-verbal_mwe=1]").attr("onClick",'')
    }
    else if (annotation_state === 4) {
        // comment annotation
        disable_core_elements();
        $('#slider_child').prop('disabled', false);
        //$('#slider_mwc').prop('disabled', false);
        //$('#slider_core_element').prop('disabled', false);
        $("#slider_mwc").prop("checked", true);
        $("#slider_core_element").prop("checked", true);
        //document.getElementById("short_instruction").innerText = "5-6) Comment your annotation";
        //document.getElementById("instruction_sentence").classList.add("hidden_element");
        document.getElementById("frame_type_selection").classList.add("hidden_element");
        document.getElementById("back_button").classList.remove("hidden_element");
        document.getElementById("mwe_block").classList.add("hidden_element");
        //document.getElementById("instruction_mwe").classList.add("hidden_element");
        //document.getElementById("instruction_core").classList.add("hidden_element");
        document.getElementById("certainty").classList.remove("hidden_element");
        document.getElementById("comment_area").classList.remove("hidden_element");
        document.getElementById("save_area").classList.remove("hidden_element");
        document.getElementById("next_area").classList.add("hidden_element");
        document.getElementById("slider_higlight_area").classList.remove("hidden_element");
        document.getElementById("skip_button").classList.add("hidden_element");
        document.getElementById("skip_reason").classList.add("hidden_element");
        document.getElementById("sentence_presentation").classList.remove("hidden_element");
        document.getElementById("current_frame_state").classList.remove("hidden_element");
        document.getElementById("summary").classList.add("hidden_element");
        document.getElementById("short_instruction").innerText = '';
    }
    else {
        // comment annotation
        disable_core_elements();
        $("#slider_mwc").prop("checked", true);
        $("#slider_core_element").prop("checked", true);
        $('#slider_child').prop('disabled', false);
        //$('#slider_mwc').prop('disabled', false);
        //$('#slider_core_element').prop('disabled', false);
        //document.getElementById("short_instruction").innerText = "5-6) Comment your annotation";
        //document.getElementById("instruction_sentence").classList.add("hidden_element");
        document.getElementById("frame_type_selection").classList.add("hidden_element");
        document.getElementById("back_button").classList.remove("hidden_element");
        document.getElementById("mwe_block").classList.add("hidden_element");
        //document.getElementById("instruction_mwe").classList.add("hidden_element");
        //document.getElementById("instruction_core").classList.add("hidden_element");
        document.getElementById("certainty").classList.add("hidden_element");
        document.getElementById("comment_area").classList.add("hidden_element");
        document.getElementById("save_area").classList.remove("hidden_element");
        document.getElementById("next_area").classList.add("hidden_element");
        document.getElementById("slider_higlight_area").classList.remove("hidden_element");
        document.getElementById("skip_button").classList.add("hidden_element");
        document.getElementById("skip_reason").classList.add("hidden_element");
        document.getElementById("sentence_presentation").classList.remove("hidden_element");
        document.getElementById("current_frame_state").classList.remove("hidden_element");
        document.getElementById("summary").classList.remove("hidden_element")
    }
}



$(document).keypress(function (e) {
 var key = e.which;
 var commentbox = document.getElementById("comment");
 if(key === 13 && ($("#annotation_state").val() <= 3) && !(($("#myModal").data("bs.modal") || {}).isShown || ($("#addElements").data("bs.modal") || {}).isShown)) // the enter key code
  {
    $('#next_button').click();
    return false;
  }
  else if (key === 13 && !(document.activeElement === commentbox) && ($("#annotation_state").val() > 3)) {
      $("#save_button").click();

 }
});