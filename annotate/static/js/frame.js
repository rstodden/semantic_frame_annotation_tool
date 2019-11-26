/* storing time when starting */
/*$(document).ready(function() {
  start = new Date();
  $("#table_annotated_records").tablesorter({dateFormat: 'ddmmyyyy'}).tablesorterPager({container: $("#pager"), size:26, widget: ["saveSort"], widgetOptions: {saveSort: true}});
  $("#table_skipped_records").tablesorter({dateFormat: 'ddmmyyyy'}).tablesorterPager({container: $("#pager_skip"), size:26, widget: ["saveSort"], widgetOptions: {saveSort: true}});
  $("#table_progress_records").tablesorter({dateFormat: 'ddmmyyyy'}).tablesorterPager({container: $("#pager_progress"), size:26, widget: ["saveSort"], widgetOptions: {saveSort: true}});
  $("#table_unannotated_records").tablesorter({dateFormat: 'ddmmyyyy'}).tablesorterPager({container: $("#pager_unannotated"), size:51, widget: ["saveSort"], widgetOptions: {saveSort: true}});

});*/


jQuery.loadScript = function (url, callback) {
    jQuery.ajax({
        url: url,
        dataType: 'script',
        success: callback,
        async: true
    });
};

tok_ids_of_mwes = [];
lemma_of_mwes = [];


function create_new_core_type_textfield(id_of_parent, id_of_element, name, change_type) {
    var parent_element = document.getElementById(id_of_parent);
    var new_slot_type = document.createElement("input");
    new_slot_type.setAttribute('id', id_of_element);
    new_slot_type.setAttribute('type', "radio");
    new_slot_type.setAttribute('value', "other");
    new_slot_type.setAttribute('name', name);
    new_slot_type.setAttribute("class", "slot-type");
    var slot_type_textfield = document.createElement("input");
    slot_type_textfield.setAttribute("type", "text");
    slot_type_textfield.setAttribute("name", "other_core_type_"+change_type);
    slot_type_textfield.setAttribute("id", "other_core_type_"+change_type);
    slot_type_textfield.setAttribute("placeholder", "choose or define a type");
    slot_type_textfield.setAttribute("onkeydown", "if (event.keyCode == 13) {return false;}");

    parent_element.appendChild(new_slot_type);
    parent_element.appendChild(slot_type_textfield);
    slot_type_textfield.onkeypress = function () {
        check_radio_button(id_of_element);
    };
    parent_element.appendChild(document.createElement("br"));

}

function create_new_core_types(id_of_parent, id_of_element, definition, value, name, bool_checked) {
    var div_add_slot_types = document.getElementById(id_of_parent);
    var new_slot_type = document.createElement("input");
    new_slot_type.setAttribute('id', id_of_element);
    new_slot_type.setAttribute('type', "radio");
    new_slot_type.setAttribute('value', value);
    new_slot_type.setAttribute('name', name);
    new_slot_type.setAttribute("class", "slot-type");
    if (bool_checked === true) {
        new_slot_type.checked = true;
    }
    var label_new_slot_type = document.createElement("label");
    label_new_slot_type.setAttribute("for", id_of_element);
    label_new_slot_type.textContent = value;

    div_add_slot_types.appendChild(new_slot_type);
    div_add_slot_types.appendChild(label_new_slot_type);

    if (definition !== '' && definition !== 'null' && definition !== null) {
        /*var new_defintion = document.createElement("abbr");
        new_defintion.setAttribute('title', definition);
        new_defintion.innerHTML = "&#9432;";*/
        var new_defintion = document.createElement("span");
        new_defintion.setAttribute("data-toggle", "tooltip");
        new_defintion.setAttribute("data-original-title", definition);
        new_defintion.setAttribute("class", "info_icon");
        new_defintion.innerHTML = "&#9432;";
        //<span data-toggle="tooltip" data-placement="right" data-original-title="resolution of discourse resolution" class="info_icon">&#9432;</span>
        div_add_slot_types.appendChild(new_defintion);
    }
    $('[data-toggle="tooltip"]').tooltip({ trigger: 'click'});


    div_add_slot_types.appendChild(document.createElement("br"));
}


function save_mwe(check_overlapping=true, element) {
    element.disabled = true;
    $.ajax({
        url: "frame",
        method: "POST",
        cache: false,
        data: {
            change_type: "save_mwe",
            check_overlapping_mwes: check_overlapping,
            mwe_components: tok_ids_of_mwes,
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
                if (data.identical_mwe && !data.overlapping_mwe) {
                    swal({
                          title: "Multiword unit already exists.",
                          text: "The chosen multiword unit was already created before and can be used in the next steps.",
                          icon: "warning",
                          buttons: true,
                          dangerMode: true,
                        });
                    element.disabled = false
                }
                else {
                    //console.log(data.list_of_slots);
                    //console.log(data);
                    if (data.changes == "new mwe created") {
                        show_new_mwe(data, core_element=false);
                    }
                    else if (data.changes == "mwe created and slot extended") {
                        show_new_mwe(data, core_element=true)
                        // reset values
                        $("input[name=slot_type_form]:checked").prop('checked', false);

                        //close the modal window
                        $('#myModal').modal('hide');

                        var references = [];
                        //$("#role_text_edit").val('');
                        $("input[name=reference_edit]:checked").prop('checked', false);
                    }
                    else if (data.changes == "mwe extended and slot extended") {
                        $("#mwe_"+data.previous_mwe_id).remove()
                        show_new_mwe(data, core_element=true, mwe_extended=true);
                        // reset values
                        $("input[name=slot_type_form]:checked").prop('checked', false);

                        //close the modal window
                        $('#myModal').modal('hide');

                        var references = [];
                        //$("#role_text_edit").val('');
                        $("input[name=reference_edit]:checked").prop('checked', false);
                    }
                    else if (data.changes == "mwe created and slots deleted"){
                        show_new_mwe(data, core_element=false);
                        for (var i = 0; i < data.list_slot_tok_ids.length; i++) {
                            console.log(data.list_slot_tok_ids[i])
                            delete_core_elements(data.list_slot_tok_ids[i], $("[data-token_id="+data.list_slot_tok_ids[i]+"]").attr("data-position"));
                        }
                        for (var n = 0; n < data.deleted_slots.length; n++) {
                            delete_core_representation(data.deleted_slots[n]);
                        }
                    }

                    // enable slider
                    $("#slider_mwc").prop("checked", true);
                    $("#slider_core_element").prop("checked", true);
                    change_color_token();

                    document.getElementById("mwe_save_button").classList.add("hidden_element");
                    document.getElementById("next_area").classList.remove("hidden_element");
                    tok_ids_of_mwes = [];
                    lemma_of_mwes = [];
                    //console.log("mwe_id", data.mwe_id);
                    element.disabled = false;
                    return data.mwe_id;
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
        },
        complete: function (jqXHR, textStatus) {
        }

    });
}


function show_new_mwe (data, core_element=false, mwe_extended=false) {
    // create new line and generate old lines as well
    $('button[name=mwe_component]').remove();
    var mwc = $("span[class*=multiword_component]");
    mwc.removeClass("multiword_component");
    mwc.addClass("multiword_expression");
    mwc.attr("data-annotation", "multiword_expression");
    mwc.attr("data-mwe", 1);
    if (core_element) {
        console.log("core_element", core_element)
        mwc.attr("data-core_element", 1);
        document.getElementById('core_element_slot_type_' + data.extended_slot).textContent = data.slot_type;
        //document.getElementById('core_element_semantic_role_' + data.extended_slot).textContent = "/ "+data.semantic_role;
        document.getElementById('core_element_lemma_' + data.extended_slot).textContent = data.lemma;
        document.getElementById('core_element_slot_type_' + data.extended_slot).id = 'core_element_slot_type_' + data.new_core_element_id;
        document.getElementById('representation_core_element_' + data.extended_slot).id = 'representation_core_element_' + data.new_core_element_id;
        document.getElementById('core_element_lemma_' + data.extended_slot).id = 'core_element_lemma_' + data.new_core_element_id;
        //document.getElementById('core_element_semantic_role_' + data.extended_slot).id = 'core_element_semantic_role_' + data.new_core_element_id;
        console.log(tok_ids_of_mwes, tok_ids_of_mwes.length);
        for (var n = 0; n < tok_ids_of_mwes.length; n++) {
            var core_element_sent = $("[data-token_id="+tok_ids_of_mwes[n]+"]");
            core_element_sent.attr("id", "core_element_"+tok_ids_of_mwes[n]);
            core_element_sent.attr('data-id', data.new_core_element_id);
            core_element_sent.attr('title', data.slot_type);
            core_element_sent.attr('data-annotation', "core_element");
            core_element_sent.attr('data-core_element', 1);
            core_element_sent.attr('data-mwe', 1);
        }

    }

    var mwe_list = document.getElementById("mwe_list");
    var new_mwe = document.createElement("li");
    new_mwe.id = "mwe_"+data.mwe_id;
    if (mwe_extended) {
        new_mwe.innerText = data.lemma;
    }
    else {
        new_mwe.innerText = lemma_of_mwes.join(' ')+' ';
    }
    var mwe_delete_button = document.createElement("button");
    mwe_delete_button.name="mwe_delete";
    mwe_delete_button.id="mwe_delete_"+data.mwe_id;
    mwe_delete_button.innerText = "delete";
    mwe_delete_button.value = data.mwe_id;
    mwe_delete_button.type = "button";
    $(mwe_delete_button).attr("onClick","delete_multiword_expression("+data.mwe_id+", check_overlapping=true)");

    console.log(data.mwe_verb);
    if (data.mwe_verb) {
        $("[name=verb_addition]").text(data.verb_addition);
        mwc.attr("data-verbal_mwe",1);
        mwc.addClass("verb");
    }

    new_mwe.appendChild(mwe_delete_button);
    mwe_list.appendChild(new_mwe);
}



function set_selection_of_core_element_types(token_id, token_word_form, token_lemma, token_position, mwe_id=null) {
    annotation_state = parseInt(document.getElementById("annotation_state").value);
    //console.log("set_selection", annotation_state);
    if (annotation_state === 1) {
        // enable mwe annotation
        if (!(tok_ids_of_mwes.includes(token_id))) {
            var mwe_representation = document.getElementById("mwe_representation");
            var new_mwe_component = document.createElement("button");
            new_mwe_component.type = "button";
            new_mwe_component.innerHTML = token_lemma;
            new_mwe_component.value = token_id;
            new_mwe_component.name = "mwe_component";
            new_mwe_component.id = "mwe_component_"+token_id;
            new_mwe_component.className ="mwe_component";
            mwe_representation.appendChild(new_mwe_component);
            var mwc = $("span[data-token_id="+token_id+"]");
            //mwc.addClass("multiword_component");
            if (mwc.hasClass("add_button")) {
                mwc.attr("class", "add_button multiword_component")
            }
            else if (mwc.hasClass("edit_button")) {
                mwc.attr("class", "edit_button multiword_component")
            }
            //mwc.attr("data-annotation", "multiword_component");
            tok_ids_of_mwes.push(token_id);
            lemma_of_mwes.push(token_lemma);
        }
        else {
            $('button[id=mwe_component_'+token_id+']').remove();
            var mwc = $("span[data-token_id="+token_id+"]");
            //todo: add here if verb is in mwe?
            //mwc.attr("data-annotation", "token");
            mwc.removeClass("multiword_component");

            var index = tok_ids_of_mwes.indexOf(token_id);
            if (index > -1) {
              tok_ids_of_mwes.splice(index, 1);
              lemma_of_mwes.splice(index, 1)
            }

            change_color_token();
        }

        if ($("button[name=mwe_component]").length > 1) {
            document.getElementById("mwe_save_button").classList.remove("hidden_element");
            document.getElementById("next_area").classList.add("hidden_element");
        }
        else {
            document.getElementById("mwe_save_button").classList.add("hidden_element");
            document.getElementById("next_area").classList.remove("hidden_element");
        }
        //console.log(tok_ids_of_mwes);
    }
    else if (annotation_state === 3) {
        // set types for core elements
        // add current token to headline
        var field_core_element_name = document.getElementById('core_element_name_edit');
        field_core_element_name.textContent = token_word_form;
        document.getElementById('core_element_name_add').textContent =token_word_form;

        var frame_type = $("input[name=f-type]:checked").val();
        // check if frame type is selected and not empty
        if (frame_type === undefined) {
            swal('Frame type missing', 'Please choose a frame type.', "warning");
            return false;
        }
        else if (frame_type === "other" && $("input[name=f-type_other_text]").val() === "") {
            swal('Frame type missing', 'Please choose a frame type.', "warning");
            return false;
        }


        else {
           // console.log(frame_type);
            $.ajax({
                url: "frame",
                method: "POST",
                cache: false,
                data: {
                    f_type: frame_type,
                    token_position: token_position,
                    mwe_id: mwe_id,
                    //frame_number: $("#frame_number").val(),
                    //f_type_other_text: $("input[name=f-type_other_text]").val(),
                    token_id: token_id,
                    change_type: "change_core_types",
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
                        //console.log(data.dict_mwes, data.count_mwes, data.dict_mwes[Object.keys(data.dict_mwes)[0]])
                        if (data.count_mwes > 1 && mwe_id === null) {
                            var new_modal = document.createElement("div");
                            new_modal.id = "new_modal";
                            for (var mwe in data.dict_mwes) {
                                var new_button = document.createElement("button");
                                new_button.id = "new_button_" + mwe;
                                new_button.type = "button";
                                new_button.value = mwe;
                                new_button.innerText = data.dict_mwes[mwe];

                                $(new_button).attr("onClick", "set_selection_of_core_element_types('" + token_id + "', '" + token_word_form + "', '" + token_lemma + "','" + token_position + "','" + mwe + "'); $('#new_modal').dialog('close');");
                                new_modal.appendChild(new_button);

                            }

                            $(new_modal).dialog({title: "Which multiword unit?"});

                        }

                        else {
                            change_frame_name_in_frontend(data.frame_type);
                            //var div_add_core_element = document.getElementById('add_core_element');
                            // get all possible slot types
                            all_slot_types = data.all_slot_types;
                            //all_semantic_roles = data.semantic_roles;
                            // loading autocompete script again after building text fields, because the function can't be assigned before
                            $.loadScript('static/js/auto_complete_functions.js', function () {
                            });

                            var div_add_slot_types = document.getElementById('div_add_slot_type');
                            var div_edit_slot_types = document.getElementById('div_edit_slot_type');
                            div_add_slot_types.innerHTML = "";
                            div_edit_slot_types.innerHTML = "";

                            // create element for handwritten type
                            if (!jQuery.isEmptyObject(data.additional_core_type)) {
                                // console.log(data.additional_core_type.name, data.additional_core_type['name']);
                                // add elements
                                //create_new_core_types('div_add_slot_type', "slot_type_form_-1_add", '', data.additional_core_type['name'], "slot_type_form_add", data.additional_core_type['checked']);

                                // edit elements
                                create_new_core_types('div_edit_slot_type', "slot_type_form_-1_edit", '', data.additional_core_type['name'], "slot_type_form_edit", data.additional_core_type['checked']);
                            }
                            for (var core_type in data["selection_core_types"]) {
                                if (data["selection_core_types"].hasOwnProperty(core_type)) {
                                    var value = core_type;
                                    var definition = data["selection_core_types"][core_type]["definition"];
                                    var id = data["selection_core_types"][core_type]["id"];

                                    // add elements
                                    create_new_core_types('div_add_slot_type', "slot_type_form_" + data["selection_core_types"][core_type]["id"] + "_add", definition, value, "slot_type_form_add", data["selection_core_types"][core_type]["checked"]);

                                    // edit elements
                                    create_new_core_types('div_edit_slot_type', "slot_type_form_" + data["selection_core_types"][core_type]["id"] + "_edit", definition, value, "slot_type_form_edit", data["selection_core_types"][core_type]["checked"]);
                                }

                            }

                            // add an textfield with new core type option
                            create_new_core_type_textfield("div_add_slot_type", "slot_type_form_other_add", "slot_type_form_add", 'add');

                            // add an textfield with new core type option
                            create_new_core_type_textfield("div_edit_slot_type", "slot_type_form_other_edit", "slot_type_form_edit", 'edit');

                            // loading autocompete script again after building text fields, because the function can't be assigned before
                            $.loadScript('static/js/auto_complete_functions.js', function () {
                            });
                            var current_element = $("span[data-position="+token_position+"]");
                            if (current_element.attr("data-annotation") === "core_element") {
                                if (data.count_mwes === 1) {
                                    $("#core_element_name_edit").text(data.dict_mwes[Object.keys(data.dict_mwes)[0]]);
                                }
                                $('#myModal').modal('show');
                                if (data.c_ref === true) {
                                    $("#reference_c_edit").prop('checked', true);
                                }
                                else {
                                    $("#reference_c_edit").prop('checked', false);
                                }
                                if (data.d_ref === true) {
                                    $("#reference_d_edit").prop('checked', true);
                                }
                                else {
                                    $("#reference_d_edit").prop('checked', false);
                                }
                                if (data.r_ref === true) {
                                    $("#reference_r_edit").prop('checked', true);
                                }
                                else {
                                    $("#reference_r_edit").prop('checked', false);
                                }
                                console.log("delete old referencens")
                            }
                            else {
                                if (data.count_mwes === 1) {
                                    $("#core_element_name_add").text(data.dict_mwes[Object.keys(data.dict_mwes)[0]]);
                                }
                                $('#addElements').modal('show');
                                if (data.c_ref) {
                                    $("#reference_c_add").prop('checked', true);
                                }
                                else {
                                    $("#reference_c_add").prop('checked', false);
                                }
                                if (data.d_ref) {
                                    $("#reference_d_add").prop('checked', true);
                                }
                                else {
                                    $("#reference_d_add").prop('checked', false);
                                }
                                if (data.r_ref) {
                                    $("#reference_r_add").prop('checked', true);
                                }
                                else {
                                    $("#reference_r_add").prop('checked', false);
                                }
                            }

                        }
                    }

                },
                error: function (jqXHR, textStatus, errorThrown) {
                    //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
                    /*swal("Error: " + errorThrown
                        + "\nStatus: " + textStatus
                        + "\njqXHR: " + JSON.stringify(jqXHR)
                    );*/
                    swal("Error. Please contact the system operator.")
                },
                complete: function (jqXHR, textStatus) {
                }

            });
        }
    }
}


function delete_core_element(element) {
    swal({
          title: "Are you sure?",
          text: "Do you want to delete the core element?",
          icon: "warning",
          buttons: true,
          dangerMode: true,
        })
        .then((willDelete) => {
            if (willDelete) {
                element.disabled = true;
                document.getElementById("save_button_edit").disabled = true;
                document.getElementById("cancel_button_edit").disabled = true;
                $.ajax({
                    url: "frame",
                    method: "POST",
                    cache: false,
                    data: {
                        //core_element_id: delete_id,
                        //token_id: token_id,
                        //frame_number: $("#frame_number").val(),
                        change_type: "delete",
                        delete_slot_of_mwe: 0,
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
                            if (data.mwe_or_tok === "token") {
                                delete_core_elements(data.token_ids, data.token_positions);
                            }
                            else {
                                var splitted_token_ids = data.token_ids.split(';');
                                var splitted_positions = data.token_positions.split(';');

                                for (var i = 0; i < splitted_token_ids.length; i++) {
                                    delete_core_elements(splitted_token_ids[i], splitted_positions[i]);
                                }
                            }

                            delete_core_representation(data.old_core_element_id);
                            $('#myModal').modal('hide');
                            change_color_token();
                            element.disabled = false;
                            document.getElementById("save_button_edit").disabled = false;
                            document.getElementById("cancel_button_edit").disabled = false;
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
                        document.getElementById("save_button_edit").disabled = false;
                        document.getElementById("cancel_button_edit").disabled = false;
                    },
                    complete: function (jqXHR, textStatus) {
                    }
                });
            }
        });
}

function show_token_details(element_id) {
	var popup = document.getElementById("token_popup_"+element_id);
	popup.classList.toggle("show");
}


function changes_saved() {
    if ($("input[name=f-type]:checked").val() === undefined) {
       // console.log('stop');
        swal('Frame type missing', 'Please choose a frame type.', "warning");
        return false;
    }
    else if ($("input[name=f-type]:checked").val() === "other" && $("input[name=f-type_other_text]").val() === "") {
        swal('Frame type missing', 'Please choose a frame type.', "warning");
        return false;
    }
    else {
        document.getElementById("save_button").disabled = true;
        document.getElementById("back_button_save").disabled = true;
        var children = $("#representation_core_element").children();
        var all_fes = [];
        for (var i = 0; i < children.length; i++) {
            if (children[i].id.startsWith("representation_core_element_")) {
                var tableChild = children[i];
                var fe = children[i].getElementsByTagName('mtd')[0].getElementsByClassName("representation_slot_type")[0];
                if (fe !== undefined) {
                    if (all_fes.includes(fe.innerHTML)) {
                        $("#slider_draft").prop("checked", true);
                        document.getElementById("save_button").disabled = false;
                        document.getElementById("back_button_save").disabled = false;
                        return confirm("It is unsual to annotate the same core element twice. Press 'OK' to save the annotation as a draft or 'Cancel' to change the annotation.")
                    }
                    else {
                        all_fes.push(fe.innerHTML);
                    }
                }
            }

        }
        console.log(all_fes);
        document.getElementById("save_button").disabled = false;
        document.getElementById("back_button_save").disabled = false;
        return true;
    }
}


function change_core_element() {
    document.getElementById("save_button_edit").disabled = false;
    document.getElementById("cancel_button_edit").disabled = false;
    document.getElementById("delete_button_edit").disabled = false;
   // console.log($("input[name=slot_type_form_edit]:checked").val(), $("input[name=other_core_type_edit]").val());
    if ($("input[name=slot_type_form_edit]:checked").val() === undefined) {
        swal('Slot type missing', 'Please choose a slot type.', "warning");
    }
    else if ($("input[name=slot_type_form_edit]:checked").val() === "other" && $("input[name=other_core_type_edit]").val() === '') {
        swal('Slot type missing', 'Please insert a slot type value.', "warning");
    }
    else if ($("#add_custom_element_types").val()==="False" && $("input[name=slot_type_form_edit]:checked").val() === "other" && !all_slot_types.includes($("input[name=other_core_type_edit]").val())) {
        swal("Wrong slot type", "Please change the slot type, currently it matches none of the non-core elements.", "warning")
    }
    /*else if ($("#role_text_edit").val() === '') {
        swal('Semantic role label missing', 'Please insert a semantic role.', "warning");
    }*/

    else {
        if ($("input[name=slot_type_form_edit]:checked").val() === "other") {
            var slot_type = $("input[name=other_core_type_edit]").val();
        }
        else {
            var slot_type = $("input[name=slot_type_form_edit]:checked").val();
        }
        if ($("input[name=f-type]:checked").val() === "other") {
            var frame_type = $("input[id=f-type_other_text]").val();
        }
        else {
            var frame_type = $("input[name=f-type]:checked").val();
        }
        var references = [];
        $("input[name=reference_edit]:checked").each(function() {
            references.push($(this).val());
        });
        document.getElementById("save_button_edit").disabled = true;
        document.getElementById("cancel_button_edit").disabled = true;
        document.getElementById("delete_button_edit").disabled = true;
        $.ajax({
            url: "frame",
            method: "POST",
            cache: false,
            data: {
                //position: core_element_position,
                slot_type: slot_type, //$("input[name=slot_type_form_edit]:checked").val(),
                f_type: frame_type, //$("input[name=f-type]:checked").val(),
                //frame_number: $("#frame_number").val(),
                change_type: "edit",
                references: references,
                //role_label: $("#role_text_edit").val(),
                //core_element_id: core_element_id,
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
                    // change values
                   // console.log('core_element_slot_type_' + data.old_core_element_id, data.slot_type);
                    document.getElementById('core_element_slot_type_' + data.old_core_element_id).textContent = data.slot_type;
                    //document.getElementById('core_element_semantic_role_' + data.old_core_element_id).textContent = "/ "+data.semantic_role;
                    document.getElementById('core_element_slot_type_' + data.old_core_element_id).id = 'core_element_slot_type_' + data.new_core_element_id;
                    document.getElementById('representation_core_element_' + data.old_core_element_id).id = 'representation_core_element_' + data.new_core_element_id;
                    document.getElementById('core_element_lemma_' + data.old_core_element_id).id = 'core_element_lemma_' + data.new_core_element_id;
                    //document.getElementById('core_element_semantic_role_' + data.old_core_element_id).id = 'core_element_semantic_role_' + data.new_core_element_id;

                    var core_element_sent = $("#core_element_" + data.token_id);
                    core_element_sent.attr('data-id', data.new_core_element_id);
                    core_element_sent.attr('title', data.slot_type);
                    core_element_sent.attr('data-annotation', "core_element");
                    core_element_sent.attr('data-core_element', 1);
                    //core_element_sent.attr('data-mwe', 1);
                    // reset values
                    $("input[name=slot_type_form]:checked").prop('checked', false);

                    //close the modal window
                    $('#myModal').modal('hide');

                    var references = [];
                    //$("#role_text_edit").val('');
                    $("input[name=reference_edit]").prop('checked', false);
                    change_color_token();
                    document.getElementById("save_button_edit").disabled = false;
                    document.getElementById("cancel_button_edit").disabled = false;
                    document.getElementById("delete_button_edit").disabled = false;
                }

            },
            error: function (jqXHR, textStatus, errorThrown) {
                //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
                /*swal("Error: " + errorThrown
                    + "\nStatus: " + textStatus
                    + "\njqXHR: " + JSON.stringify(jqXHR)
                );*/
                swal("Error. Please contact the system operator.");
                document.getElementById("save_button_edit").disabled = false;
                document.getElementById("cancel_button_edit").disabled = false;
                document.getElementById("delete_button_edit").disabled = false;
            },
            complete: function (jqXHR, textStatus) {
            }

        });
    }
}


function add_core_element() {
    document.getElementById("save_button_add").disabled = false;
    document.getElementById("cancel_button_add").disabled = false;
   //console.log($("input[name=slot_type_form_add]:checked").val(), $("input[name=mwc]:checked").val());
    var slot_type_value = $("input[name=slot_type_form_add]:checked").val();
    var multiword_component = $("input[name=mwc]:checked").val();
    /*if (slot_type_value !== undefined) { //}) && multiword_component !== undefined) {
        swal('Select a slot type or multiword component',"You can't choose a slot type and multiword component at the same type. Please choose only one of them.", "warning");
    }*/
    if (slot_type_value === undefined) { //} && multiword_component === undefined) {
        swal('Slot type missing','Please choose a slot type.', "warning");
    }
    else if (slot_type_value === "other" && $("input[name=other_core_type_add]").val() === '') {
        swal('Slot type missing','Please insert a slot type value.', "warning");
    }
    else if ($("#add_custom_element_types").val()==="False" && slot_type_value === "other" && !all_slot_types.includes($("input[name=other_core_type_add]").val())) {
        swal("Wrong slot type", "Please change the slot type, currently it matches none of the non-core elements.", "warning")
    }
    /*else if ($("#role_text_add").val() === '') {
        swal('Semantic role label missing', 'Please insert a semantic role.', "warning");
    }*/
    else {

        if (slot_type_value === "other") {
            var slot_type = $("input[name=other_core_type_add]").val();
        }
        else {
            var slot_type = slot_type_value;
        }
        /*if ($("input[name=f-type]:checked").val() === "other") {
            var frame_type = $("input[id=f-type_other_text]").val();
        }
        else {
            var frame_type = $("input[name=f-type]:checked").val();
        }*/
        var references = [];
        $("input[name=reference_add]:checked").each(function() {
            references.push($(this).val());
        });

        document.getElementById("save_button_add").disabled = true;
        document.getElementById("cancel_button_add").disabled = true;
        //console.log(references);
       // console.log("frame", frame_type, "slot", slot_type);
        $.ajax({
            url: "frame",
            method: "POST",
            cache: false,
            data: {
                //word_form: core_element_add_word_form,
                //position: core_element_add_position,
                slot_type: slot_type,
                //f_type: frame_type,
                //multiword_component: multiword_component,
                //frame_number: $("#frame_number").val(),
                change_type: "add",
                references: references,
                //role_label: $("#role_text_add").val(),
                //core_element_id: core_element_id,
                csrfmiddlewaretoken: jQuery("[name=csrfmiddlewaretoken]").val(),
                dataType: 'json'
            },
            success: function (data) {
               // console.log(data.new_core_element, data.id, data.token_id, "coreelement id");
                // data entspricht rueckgabewert aus backend views
                if (typeof data.error !== 'undefined') {
                    // ausfuehren wenn in data kein ergebnis zur suchanfrage gefunden
                    swal('something went wrong', data["error"], "error");
                }
                else {
                    // set new frame_id
                    //document.getElementById("frame_number").value = data.frame_id;
                    //console.log(document.getElementById("frame_number").value, 'here', data.frame_id);

                    // add values
                    //var id_core_element = data.id;
                    if (data.multiword_component === true) {
                        //console.log("MWC", data);

                        set_slot_representation(data.id, data.slot_type, data.word_form, "mwe");

                        $("input[name=slot_type_form_add]:checked").prop('checked', false);

                        //close the modal window
                        $('#addElements').modal('hide');

                        var splitted_token_ids = data.token_id.split(';');
                        var splitted_positions = data.position.split(';');

                        for (var i = 0; i < splitted_token_ids.length; i++) {
                            set_token_element_to_slot(splitted_positions[i], splitted_token_ids[i], data.id, data.slot_type, "mwe");
                        }

                        //close the modal window
                        $('#addElements').modal('hide');
                    }
                    else {
                        set_slot_representation(data.id, data.slot_type, data.word_form, "tok");


                        $("input[name=slot_type_form_add]:checked").prop('checked', false);

                        // enable slider
                        $("#slider_core_element").prop("checked", true);
                        change_color_token();

                        // change class of element
                        set_token_element_to_slot(data.position, data.token_id, data.id, data.slot_type, "tok");

                        //close the modal window
                        $('#addElements').modal('hide');
                    }
                    var references = [];
                    //$("#role_text_add").val('');
                    $("input[name=reference_add]").prop('checked', false);
                    change_color_token();
                    document.getElementById("save_button_add").disabled = false;
                    document.getElementById("cancel_button_add").disabled = false;

                }

            },
            error: function (jqXHR, textStatus, errorThrown) {
                //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
                /*swal("Error: " + errorThrown
                    + "\nStatus: " + textStatus
                    + "\njqXHR: " + JSON.stringify(jqXHR)
                );*/
                swal("Error. Please contact the system operator.");
                document.getElementById("save_button_add").disabled = false;
                document.getElementById("cancel_button_add").disabled = false;
            },
            complete: function (jqXHR, textStatus) {
            }

        });
    }
}


function set_slot_representation(core_element_id, slot_type, word_form, component_type) {
    var core_elements_span = document.getElementById('core_elements');
    var new_core_element = document.createElement("span");
    new_core_element.setAttribute('id', "core_element_" + core_element_id);
    new_core_element.innerHTML = '<b>Slot type: </b><span id="core_element_slot_type_' + core_element_id + '">' +
        slot_type + '</span>, <b>word form:</b> <span id="core_element_wordform_' + core_element_id + '">' +
        word_form + '</span>';
    var core_elements_table = document.getElementById('representation_core_element');
    var new_slot_type_row = document.createElement("mtr");
    new_slot_type_row.setAttribute('id', 'representation_core_element_' + core_element_id);
    var new_slot_type_element = document.createElement("mtd");
    var new_slot_type = document.createElement("mi");
    new_slot_type.setAttribute('class', 'representation_slot_type');
    new_slot_type.setAttribute('id', 'core_element_slot_type_' + core_element_id);
    new_slot_type.textContent = slot_type;
    new_slot_type_element.appendChild(new_slot_type);

    var new_word_form_element = document.createElement("mtd");
    var new_word_form = document.createElement('mi');
    new_word_form.setAttribute('class', 'representation_word_form');
    new_word_form.setAttribute('id', 'core_element_lemma_' + core_element_id);
    new_word_form.textContent = word_form;
    new_word_form_element.appendChild(new_word_form);

    /*var new_semantic_role = document.createElement('mi');
    new_semantic_role.setAttribute('class', 'representation_word_form');
    new_semantic_role.setAttribute('id', 'core_element_semantic_role_' + core_element_id);
    new_semantic_role.textContent = "/ "+semantic_role;
    new_word_form_element.appendChild(new_semantic_role);*/

    new_slot_type_row.appendChild(new_slot_type_element);
    new_slot_type_row.appendChild(new_word_form_element);
    core_elements_table.appendChild(document.createElement("br"));
    core_elements_table.appendChild(new_slot_type_row);
}

function set_token_element_to_slot(position, token_id, slot_id, slot_type, component_type) {
    // change class of element
    var core_element = $("#token_" + position);
    var element = $("span[data-position="+position+"]");
    if (element.hasClass("token")) {
        element.removeClass("token");
    }
    if (element.hasClass("multiword_expression")) {
        element.removeClass("multiword_expression");
    }
    if (element.hasClass("add_button")) {
        element.removeClass("add_button");
    }
    if (element.hasClass("verb_child")) {
        element.removeClass("verb_child");
    }
    element.addClass("core_element");
    element.addClass("edit_button");
    //core_element.removeClass(document.getElementById("token_" + position).className).addClass("core_element").addClass("edit_button");
    //core_element.attr('data-target','#myModal');
    core_element.attr('data-annotation', "core_element");
    core_element.attr('data-core_element', 1);
    core_element.attr('data-token_id', token_id);
    core_element.attr('data-id', slot_id);
    core_element.attr('title', slot_type);
    change_color_token();
    // change id of element
    document.getElementById("token_" + position).id = 'core_element_' + token_id;
}


function delete_multiword_expression(mwe_id, check_overlapping=false) {
    //console.log("delete mwe");
    document.getElementById("mwe_delete_"+mwe_id).disabled = true;
    $.ajax({
        url: "frame",
        method: "POST",
        cache: false,
        data: {
            change_type: "delete_mwe",
            mwe_id: mwe_id,
            check_overlapping: check_overlapping,
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
                if (check_overlapping && data.overlapping_mwe) {
                    if (data.overlapping_mwe.length > 1) {
                        // @todo.
                        swal('Currently not implemented.', 'Please do it manually. Feature will be implemented soon.', "warning");
                    }
                    else {
                        var slot_id = Object.keys(data.list_of_slots)[0];
                        var slot = data.list_of_slots[slot_id];
                        swal({
                              title: "Multiword unit contains a core element",
                              text: "Do you also want to delete the core element '"+slot[0]+"' ("+slot[1]+")?",
                              icon: "warning",
                              buttons: true,
                              dangerMode: true,
                            })
                            .then((willDelete) => {
                                if (willDelete) {
                                    //console.log("delete both", data);
                                    $.ajax({
                                        url: "frame",
                                        method: "POST",
                                        cache: false,
                                        data: {
                                            core_element_id: slot_id,
                                            delete_slot_of_mwe: 1,
                                            //token_id: token_id,
                                            //frame_number: $("#frame_number").val(),
                                            change_type: "delete",
                                            csrfmiddlewaretoken: jQuery("[name=csrfmiddlewaretoken]").val(),
                                            dataType: 'json'
                                        },
                                        success: function (data) {
                                            //console.log("delete core",data)
                                            // data entspricht rueckgabewert aus backend views
                                            if (typeof data.error !== 'undefined') {
                                                // ausfuehren wenn in data kein ergebnis zur suchanfrage gefunden
                                                swal('something went wrong', data["error"], "error");
                                            }
                                            else {
                                                if (data.mwe_or_tok === "token") {
                                                    delete_core_elements(data.token_ids, data.token_positions);
                                                }
                                                else {
                                                    var splitted_token_ids = data.token_ids.split(';');
                                                    var splitted_positions = data.token_positions.split(';');

                                                    for (var i = 0; i < splitted_token_ids.length; i++) {
                                                        delete_core_elements(splitted_token_ids[i], splitted_positions[i]);
                                                    }
                                                }

                                                delete_core_representation(data.old_core_element_id);
                                                $('#myModal').modal('hide');

                                                delete_multiword_expression(mwe_id, check_overlapping=false);
                                            }

                                        },
                                        error: function (jqXHR, textStatus, errorThrown) {
                                            //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
                                            /*swal("Error: " + errorThrown
                                                + "\nStatus: " + textStatus
                                                + "\njqXHR: " + JSON.stringify(jqXHR)
                                            );*/
                                            swal("Error. Please contact the system operator.")
                                        },
                                        complete: function (jqXHR, textStatus) {
                                        }
                                    });

                                }
                                else {
                                    console.log("mwe not deleted.");
                                    document.getElementById("mwe_delete_"+mwe_id).disabled = false;
                                }
                            });
                        change_color_token();
                    }
                }
                else {
                    // conditions with overlapping and warning here
                    //console.log("deleted");
                    $('li[id=mwe_'+mwe_id+']').remove();
                    if (data.mwe_verb) {
                        $("[name=verb_addition]").text('');
                    }
                    for (var token_id in data.token_ids) {
                        var delete_element = $("span[data-token_id="+data.token_ids[token_id]+"]");
                        delete_element.removeClass("multiword_expression");
                        delete_element.addClass("token");
                        delete_element.attr("data-annotation", "token");
                        delete_element.attr("data-mwe", 0);
                        console.log(delete_element.attr('id'), data);
                        if (data.mwe_verb && delete_element.attr('id') !== "frame_verb") {
                            delete_element.attr("data-verbal_mwe", 0);
                            delete_element.removeClass("verb");
                            delete_element.attr('onClick', "set_selection_of_core_element_types('" + delete_element.attr("data-token_id") + "', '" + delete_element.attr("data-word_form") + "', '" + delete_element.attr("data-lemma") + "', '" + delete_element.attr("data-position") + "')");
                        }
                    }
                    change_color_token();
                    // data annotaion token
                    // class toekn
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
            document.getElementById("mwe_delete_"+mwe_id).disabled = false;
        },
        complete: function (jqXHR, textStatus) {
        }

    });
}

function edit_multiword_expression() {

}


function check_radio_button(button_id) {
    document.getElementById(button_id).checked = true;
}


function add_class_to_elements(list_elements) {
   for (var change_elements in list_elements) {
       //list_elements[i].addClass()
       if (change_elements === "token") {
           for (var elements in list_elements[change_elements]) {
               list_elements[change_elements][elements].addClass("token")
           }
       }
       else if (change_elements === "verb_child") {
           for (var elements in list_elements[change_elements]) {
               list_elements[change_elements][elements].addClass("verb_child")
           }
       }
       else if (change_elements === "multiword_expression") {
           for (var elements in list_elements[change_elements]) {
               list_elements[change_elements][elements].addClass("multiword_expression")
           }
       }
       else if (change_elements === "core_element") {
           for (var elements in list_elements[change_elements]) {
               list_elements[change_elements][elements].addClass("core_element")
           }
       }
       else if (change_elements === "child_mwe") {
           for (var elements in list_elements[change_elements]) {
               list_elements[change_elements][elements].addClass("child_mwe")
           }
       }
       else if (change_elements === "child_core_element") {
           for (var elements in list_elements[change_elements]) {
               list_elements[change_elements][elements].addClass("child_core_element")
           }
       }
       else if (change_elements === "mwe_core_element") {
           for (var elements in list_elements[change_elements]) {
               list_elements[change_elements][elements].addClass("mwe_core_element")
           }
       }
       else if (change_elements === "mwe_core_element_child") {
           for (var elements in list_elements[change_elements]) {
               list_elements[change_elements][elements].addClass("mwe_core_element_child")
           }
       }
   }
}



function remove_class_from_elements(list_elements) {
    for (var change_elements in list_elements) {
       //list_elements[i].addClass()
       if (change_elements === "token") {
           for (var elements in list_elements[change_elements]) {
               if(list_elements[change_elements][elements].hasClass('token')) {
                   list_elements[change_elements][elements].removeClass("token")
               }
           }
       }
       else if (change_elements === "verb_child") {
            for (var elements in list_elements[change_elements]) {
               if(list_elements[change_elements][elements].hasClass('verb_child')) {
                   list_elements[change_elements][elements].removeClass("verb_child")
               }
           }
       }
       else if (change_elements === "multiword_expression") {
            for (var elements in list_elements[change_elements]) {
               if(list_elements[change_elements][elements].hasClass('multiword_expression')) {
                   list_elements[change_elements][elements].removeClass("multiword_expression")
               }
           }
       }
       else if (change_elements === "core_element") {
            for (var elements in list_elements[change_elements]) {
               if(list_elements[change_elements][elements].hasClass('core_element')) {
                   list_elements[change_elements][elements].removeClass("core_element")
               }
           }
       }
       else if (change_elements === "child_mwe") {
           for (var elements in list_elements[change_elements]) {
               if(list_elements[change_elements][elements].hasClass('child_mwe')) {
                   list_elements[change_elements][elements].removeClass("child_mwe")
               }
           }
       }
       else if (change_elements === "mwe_core_element") {
           for (var elements in list_elements[change_elements]) {
               if(list_elements[change_elements][elements].hasClass('mwe_core_element')) {
                   list_elements[change_elements][elements].removeClass("mwe_core_element")
               }
           }
       }
       else if (change_elements === "mwe_core_element_child") {
           for (var elements in list_elements[change_elements]) {
               if(list_elements[change_elements][elements].hasClass('mwe_core_element_child')) {
                   list_elements[change_elements][elements].removeClass("mwe_core_element_child")
               }
           }
       }
       else if (change_elements === "child_core_element") {
           for (var elements in list_elements[change_elements]) {
               if(list_elements[change_elements][elements].hasClass('child_core_element')) {
                   list_elements[change_elements][elements].removeClass("child_core_element")
               }
           }
       }
   }
}


function change_color_token() {
    // todo: change color for multiwordcomponents
    /*var core_elements_childs = $("span[data-annotation=core_element][data-type=child]");
    var core_elements = $("span[data-annotation=core_element][data-type=token]");
    var multiword_components_childs = $("span[data-annotation=multiword_expression][data-type=child]");
    var multiword_components = $("span[data-annotation=multiword_expression][data-type=token]");
    var childs = $("span[data-annotation=token][data-type=child]");*/
    var token = $("span[data-type='token'][data-MWE='0'][data-core_element='0']");
    var child = $("span[data-type='child'][data-MWE='0'][data-core_element='0']");
    var mwe = $("span[data-type='token'][data-MWE='1'][data-core_element='0']");
    var core_element = $("span[data-type='token'][data-MWE='0'][data-core_element='1']");
    var child_mwe = $("span[data-type='child'][data-MWE='1'][data-core_element='0']");
    var child_core_element = $("span[data-type='child'][data-MWE='0'][data-core_element='1']");
    var mwe_core_element = $("span[data-type='token'][data-MWE='1'][data-core_element='1']");
    var mwe_core_element_child = $("span[data-type='child'][data-MWE='1'][data-core_element='1']");

    if (document.getElementById("slider_child").checked && document.getElementById("slider_core_element").checked && document.getElementById("slider_mwc").checked) {
        add_class_to_elements({"token":[token], "verb_child": [child], "multiword_expression":[mwe],
            "core_element": [core_element], "child_mwe": [child_mwe], "child_core_element": [child_core_element],
            "mwe_core_element": [mwe_core_element], "mwe_core_element_child": [mwe_core_element_child]});
        remove_class_from_elements({"token":[child, mwe, core_element, child_mwe, child_core_element, mwe_core_element, mwe_core_element_child],
            "verb_child": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, mwe, core_element, token],
            "core_element": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, token],
            "multiword_expression":[mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                core_element, token],
            "mwe_core_element": [mwe_core_element_child, child_mwe, child_core_element, child,
                mwe, core_element, token],
            "child_core_element": [mwe_core_element_child, mwe_core_element, child_mwe, child,
                mwe, core_element, token],
            "child_mwe": [mwe_core_element_child, mwe_core_element, child_core_element, child,
                mwe, core_element, token],
            "mwe_core_element_child": [mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token]});
    }
    else if (document.getElementById("slider_child").checked && document.getElementById("slider_core_element").checked && !document.getElementById("slider_mwc").checked) {
        add_class_to_elements({
            "token": [token, mwe], "verb_child": [child, child_mwe], "core_element": [core_element, mwe_core_element],
            "child_core_element": [child_core_element, mwe_core_element_child]
        });
        remove_class_from_elements({
            "token": [child, mwe, core_element, child_mwe, child_core_element, mwe_core_element, mwe_core_element_child],
            "multiword_expression": [mwe, mwe_core_element, mwe_core_element_child, child_mwe, token],
            "mwe_core_element": [mwe_core_element, mwe_core_element_child, mwe, token, child],
            "mwe_core_element_child": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token],
            "child_core_element": [token, child, core_element],
            "child_mwe": [child_mwe, mwe, mwe_core_element_child, mwe_core_element, token]
        });
    }
    else if (document.getElementById("slider_child").checked && !document.getElementById("slider_core_element").checked && document.getElementById("slider_mwc").checked) {
        add_class_to_elements({"token":[token, core_element],
            "verb_child": [child, child_core_element],
            "multiword_expression":[mwe, mwe_core_element],
            "child_mwe": [child_mwe, mwe_core_element_child]});
        remove_class_from_elements({"token":[child, mwe, child_mwe, mwe_core_element, mwe_core_element_child],
            "child_core_element": [child_core_element, core_element, mwe_core_element_child, token, child],
            "core_element": [core_element, child_core_element, mwe_core_element_child, mwe_core_element, token],
            "mwe_core_element": [mwe_core_element, core_element, mwe_core_element_child, token, child, mwe],
            "mwe_core_element_child": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token]});
    }
    else if (!document.getElementById("slider_child").checked && document.getElementById("slider_core_element").checked && document.getElementById("slider_mwc").checked) {
        add_class_to_elements({"token":[token, child],  "multiword_expression":[mwe, child_mwe],
            "core_element": [core_element, child_core_element],
            "mwe_core_element": [mwe_core_element, mwe_core_element_child]});
        remove_class_from_elements({
            "token":[mwe, core_element, child_mwe, child_core_element, mwe_core_element, mwe_core_element_child],
            "verb_child": [child, child_mwe, child_core_element, mwe_core_element_child, token],
            "mwe_core_element_child": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token],
            "child_core_element": [child_core_element, child_mwe, child, mwe_core_element_child, token],
            "mwe_core_element": [token, mwe, child, child_mwe],
            "multiword_expression": [mwe_core_element],
            "core_element": [mwe_core_element]});
    }
    else if (document.getElementById("slider_child").checked && !(document.getElementById("slider_core_element").checked) && !document.getElementById("slider_mwc").checked) {
        add_class_to_elements({"token":[token, mwe, core_element, mwe_core_element],
            "verb_child": [child_core_element, child_mwe, mwe_core_element_child, child]
            });
        remove_class_from_elements({"token":[child, child_mwe, child_core_element, mwe_core_element_child],
            "core_element": [core_element, mwe_core_element, mwe_core_element_child, child_core_element, token],
            "multiword_expression":[mwe, mwe_core_element, child_mwe, mwe_core_element_child, token],
            "mwe_core_element": [mwe_core_element, mwe_core_element_child, core_element, mwe, token],
            "child_core_element": [child_core_element, mwe_core_element_child, child_mwe, token, child],
            "child_mwe": [child_mwe, mwe_core_element_child, token],
            "mwe_core_element_child": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token]});
    }
    else if (!document.getElementById("slider_child").checked && !(document.getElementById("slider_core_element").checked) && document.getElementById("slider_mwc").checked) {
        add_class_to_elements({"token":[token, core_element, child, child_core_element],
            "multiword_expression":[mwe, mwe_core_element, mwe_core_element_child, child_mwe]});
        remove_class_from_elements({"token":[mwe, child_mwe, mwe_core_element, mwe_core_element_child],
            "core_element": [core_element, mwe_core_element, mwe_core_element_child, child_core_element, token],
            "mwe_core_element": [mwe_core_element, mwe_core_element_child, core_element, token],
            "child_core_element": [child_core_element, mwe_core_element_child, child_mwe, core_element, mwe_core_element, token, child],
            "child_mwe": [child_mwe, mwe_core_element_child, child, child_core_element, mwe_core_element, token],
            "verb_child": [child, child_core_element, child_mwe, mwe_core_element_child, token],
            "mwe_core_element_child": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token]
        });
    }
    else if (!document.getElementById("slider_child").checked && (document.getElementById("slider_core_element").checked) && !document.getElementById("slider_mwc").checked) {
        add_class_to_elements({"token":[token, child, mwe, child_mwe],
            "core_element": [core_element, child_core_element, mwe_core_element_child, mwe_core_element]});
        remove_class_from_elements({
            "token": [core_element, child_core_element, mwe_core_element, mwe_core_element_child],
            "multiword_expression": [mwe, mwe_core_element, mwe_core_element_child, child_mwe, token],
            "mwe_core_element": [mwe_core_element, mwe_core_element_child, child_mwe, child_core_element, token],
            "child_core_element": [child_core_element, mwe_core_element_child, child_mwe, mwe_core_element, child, child_mwe, token],
            "child_mwe": [child_mwe, mwe_core_element_child, child, child_core_element, mwe_core_element, mwe, token],
            "verb_child": [child, child_core_element, child_mwe, mwe_core_element_child, token],
            "mwe_core_element_child": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token]
        })
    }
    else if (!(document.getElementById("slider_child").checked) && !document.getElementById("slider_core_element").checked && !document.getElementById("slider_mwc").checked) {
        add_class_to_elements({"token":[child, mwe, core_element, child_mwe, child_core_element, mwe_core_element, mwe_core_element_child]});
        remove_class_from_elements({
            "verb_child": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token],
            "core_element": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token],
            "multiword_expression":[mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token],
            "mwe_core_element": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token],
            "child_core_element": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token],
            "child_mwe": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token],
            "mwe_core_element_child": [mwe_core_element_child, mwe_core_element, child_mwe, child_core_element, child,
                mwe, core_element, token]});

    }
    /*else {
        $("button[id^=core_element]").attr('class', 'token edit_button');
        $("button[name=verb_child]button[id^=token]").attr('class', 'token add_button');
    }*/
}


function save_frame_type(frame_type_name,other=false) {
    //var frame_id = document.getElementById("frame_number").value;
    if (frame_type_name === '')
    {
        swal('Frame type missing', 'Please choose a frame type.', "warning");
    }
    else {
        $.ajax({
            url: "frame",
            method: "POST",
            cache: false,
            data: {
                f_type: frame_type_name,
                other_f_type: other,
                //frame_number: frame_id,
                change_type: "save_frame_type",
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
                    // console.log("saved.", data.frame_id, data);
                    change_frame_name_in_frontend(frame_type_name);
                    //document.getElementById("frame_number").value = data.frame_id;
                    //console.log(document.getElementById("frame_number").value);
                    if (!jQuery.isEmptyObject(data.delete_elements)) {
                        for (var delete_id in data.delete_elements) {
                            if (data.delete_elements.hasOwnProperty(delete_id)) {
                                if (data.delete_elements[delete_id].hasOwnProperty("token_id")) {
                                    var token_id = data.delete_elements[delete_id]['token_id'];
                                    var token_position = data.delete_elements[delete_id]['token_position'];
                                    delete_core_elements(token_id, token_position);
                                }
                                else if (data.delete_elements[delete_id].hasOwnProperty("mwe_id")) {
                                    var token_ids = data.delete_elements[delete_id]['token_ids'].split(';');
                                    var token_positions = data.delete_elements[delete_id]['mwe_position'].split(';');
                                    for (var i = 0; i < token_ids.length; i++) {
                                        delete_core_elements(token_ids[i], token_positions[i])
                                    }
                                }
                                delete_core_representation(delete_id);
                            }

                        }
                    }
                    if (other) {
                        var frame_type_selection = document.getElementById("frame_types_form");
                        var new_id = "f-type_" + frame_type_selection.childElementCount;
                        var new_label = document.createElement("label");
                        new_label.className = "label_frame_type";
                        new_label.onclick = "check_radio_button('" + new_id + "')";
                        new_label.innerText = frame_type_name;
                        new_label.for = new_id;
                        var new_input = document.createElement("input");
                        new_input.className = "frame_type";
                        new_input.name = "f-type";
                        new_input.value = frame_type_name;
                        new_input.type = "radio";
                        new_input.checked = true;
                        new_input.id = new_id;
                        $("#" + new_id).attr('onClick', "save_frame_type('" + frame_type_name + "')");
                        /*var new_definition = document.createElement("a");
                        new_definition.href = "http://corpora.phil.hhu.de/framenet/fndata-1.7/frame/" + frame_type_name + ".xml";
                        new_definition.title = "extern frame type definition";
                        new_definition.target = "_blank";
                        new_definition.innerText = " \u24D8";*/

                        frame_type_selection.appendChild(document.createElement("br"));
                        frame_type_selection.appendChild(new_input);
                        frame_type_selection.appendChild(new_label);
                        if ($("#all_frame_types").val().includes(frame_type_name) && $("#add_custom_element_types").val() === "False") {
                            console.log($("#all_frame_types").val().includes(frame_type_name) , $("#add_custom_element_types").val() === "False");
                            var new_button = document.createElement("a");
                            new_button.title = "extern frame type definition";
                            new_button.setAttribute("target", "_blank")
                            new_button.href = "http://corpora.phil.hhu.de/framenet/fndata-1.7/frame/"+ frame_type_name+".xml"
                            new_button.innerText = " \u24D8";
                            frame_type_selection.appendChild(new_button);
                        }
                        //frame_type_selection.appendChild(new_definition);
                        document.getElementById('f-type_other_text').value = "";

                    }
                    change_color_token();
                    //close synonym div
                    $("#button_show_synonyms").attr('aria-expanded', "false").addClass("collapsed");
                    $("#frame_types_synonyms").attr('aria-expanded', "false").removeClass("in");
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
                /*swal("Error: " + errorThrown
                    + "\nStatus: " + textStatus
                    + "\njqXHR: " + JSON.stringify(jqXHR)
                );*/
                swal("Error. Please contact the system operator.")
            },
            complete: function (jqXHR, textStatus) {
            }
        });
    }
}

function change_frame_name_in_frontend(frame_type_name) {
    document.getElementById("representation_frame_name_headline").textContent = frame_type_name;
    document.getElementById("representation_frame_name").textContent = frame_type_name;
    document.getElementById("modal_edit_frame_name").textContent = frame_type_name;
    document.getElementById("modal_add_frame_name").textContent = frame_type_name;
}


function delete_core_representation(delete_id) {
    var token_to_delete = document.getElementById('representation_core_element_' + delete_id);
    if (typeof token_to_delete !== 'undefined') {
        token_to_delete.innerHTML = '';
        token_to_delete.parentNode.removeChild(token_to_delete);
    }
}

function delete_core_elements(token_id, token_position) {
    //console.log(token_id, token_position)
    // change color of token
    var core_element = $("span[data-token_id="+token_id+"]");
    //var core_element = $("#core_element_" + token_id);
    //core_element.removeClass(document.getElementById('core_element_' + token_id).className).addClass("token").addClass("add_button");
    core_element.removeClass("core_element");
    core_element.removeClass("edit_button");
    core_element.addClass("add_button");
    core_element.attr('data-annotation', "token");
    core_element.attr('data-core_element', 0);
    core_element.attr("id", "token_"+token_position);
    //core_element.addClass("token");
    var child = $("[data-token_id="+token_id+"][data-type=child]");
    child.addClass("verb_child");
    child.addClass("add_button");
    child.attr('title', 'child of verb');
    child.attr('data-annotation', "token");
    child.attr('data-core_element', 0);
}


function set_session(frame_id) {
    //var frame_id = document.getElementById("frame_number").value;
    $.ajax({
        url: "set_session",
        method: "POST",
        cache: false,
        data: {
            f_nr: frame_id,
            csrfmiddlewaretoken: jQuery("[name=csrfmiddlewaretoken]").val(),
            dataType: 'json'
        },
        success: function (data) {
            // data entspricht rueckgabewert aus backend views
            if (typeof data.error !== 'undefined') {
                // ausfuehren wenn in data kein ergebnis zur suchanfrage gefunden
                swal('something went wrong', data["error"], "error");
                return false;
            }
            else {
               // console.log("session saved.");
                return true;
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
            /*swal("Error: " + errorThrown
                + "\nStatus: " + textStatus
                + "\njqXHR: " + JSON.stringify(jqXHR)
            );*/
            swal("Error. Please contact the system operator.");
            return false
        },
        complete: function (jqXHR, textStatus) {
            return true
        }
    });
}

function skip_frame(element) {
    //console.log("skip sentence");
    element.disabled = true;
    var skip_sentence_field = $("#skip_sentence_field").val();
    if (skip_sentence_field === '') {
        swal('Reason missing', 'Please type a reason.', "warning");
        element.disabled = false;
    }
    else {
        $.ajax({
            url: "skip_sentence",
            method: "POST",
            cache: false,
            data: {
                skip_reason: skip_sentence_field,
                csrfmiddlewaretoken: jQuery("[name=csrfmiddlewaretoken]").val(),
                dataType: 'json'
            },
            success: function (data) {
                if (typeof data.error !== 'undefined') {
                    // ausfuehren wenn in data kein ergebnis zur suchanfrage gefunden
                    swal('something went wrong', data["error"], "error");
                    element.disabled = false;
                    return false;
                }
                else {
                    // console.log("session saved.");
                    $('#skipModal').modal('hide');
                    $("#skip_sentence_field").val('');
                    window.location.href = data.page_name;
                    element.disabled = false;
                    return true;
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
                swal("Error. Please contact the system operator.");
                element.disabled = false;
                return false
            },
            complete: function (jqXHR, textStatus) {
                element.disabled = false;
                return true
            }
        });
    }
}


jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
});


function rotate_arrow(name_input, name_other_header) {
    if ($("#"+name_input).hasClass('fa fa-chevron-down')) {
        $("i[name="+name_other_header+"]").removeClass("fa fa-chevron-down");
        $("i[name="+name_other_header+"]").removeClass("fa fa-chevron-up");
        $("#"+name_input).addClass('fa fa-chevron-up');
    } else if ($("#"+name_input).hasClass('fa fa-chevron-up')) {
        $("i[name="+name_other_header+"]").removeClass("fa fa-chevron-down");
        $("i[name="+name_other_header+"]").removeClass("fa fa-chevron-up");
        $("#"+name_input).addClass('fa fa-chevron-down');
    }
    else {
        $("i[name="+name_other_header+"]").removeClass("fa fa-chevron-down");
        $("i[name="+name_other_header+"]").removeClass("fa fa-chevron-up");
        $("#"+name_input).addClass('fa fa-chevron-up');
    }
}


function change_order_in_session(id_header, name_header) {
    //console.log($('#'+id_header).attr('aria-sort'));
    $.ajax({
            url: "save_sorting_order",
            method: "POST",
            cache: false,
            data: {
                id_element: id_header,
                value_element: $('#'+id_header).attr('aria-sort'),
                csrfmiddlewaretoken: jQuery("[name=csrfmiddlewaretoken]").val(),
                dataType: 'json'
            },
            success: function (data) {
                if (typeof data.error !== 'undefined') {
                    // ausfuehren wenn in data kein ergebnis zur suchanfrage gefunden
                    swal('something went wrong', data["error"], "error");
                    return false;
                }
                else {}
            },
            error: function (jqXHR, textStatus, errorThrown) {
                //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
                swal("Error. Please contact the system operator.");
                return false
            },
            complete: function (jqXHR, textStatus) {
                return true
            }
        });

}

$(function () {
  $('[data-toggle="tooltip"]').tooltip({ trigger: 'click'});
});

$(document).on("click", function (e) {
    $('[data-toggle=tooltip]').each(function () {
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            $(this).tooltip("hide");
        }
        });
    });

function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}

