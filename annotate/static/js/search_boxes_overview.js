var autocompletion_search_frame_type = new autoComplete({
    selector: '#searchbox_progress_frame',
    minChars: 0,
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


var autocompletion_search_verb = new autoComplete({
    selector: '#searchbox_progress_verb',
    minChars: 0,
    source: function(term, suggest) {
        term = term.toLowerCase();
        var choices = eval($("input[name=all_verbs]").val());
        var matches = [];
        for (i = 0; i < choices.length; i++) {
            if (~choices[i].toLowerCase().indexOf(term)) {
                matches.push(choices[i]);
                suggest(matches);
            }
        }
    }
});


function change_records_view(record_type, kind_change, value) {
    $.ajax({
        url: "frame_list",
        method: "POST",
        cache: false,
        data: {
            record_type: record_type,
            change_value: kind_change,
            value: value,
            csrfmiddlewaretoken: jQuery("[name=csrfmiddlewaretoken]").val(),
            dataType: 'json'
        },
        success: function (data) {
            // data entspricht rueckgabewert aus backend views
            if (typeof data.error !== 'undefined') {
                // ausfuehren wenn in data kein ergebnis zur suchanfrage gefunden
                swal('something went wrong', data["error"], "error");
                element.disabled = false;
            }
            else {
                //data = JSON.parse(data);
                //console.log("changed.", data["frames_annotated"][0].fields);
                var parent_of_rows = $("#searchbar_"+record_type).parent();
                $("[name=record_of_"+record_type+"]").remove();
                if (record_type!=="not_annotated_frames") {
                    for (var i = 0; i < data.length; i++){
                        var e = data[i].fields;
                        if (e.timestamp !== null) {
                            var year = e.timestamp.slice(0, 4);
                            var month = e.timestamp.slice(5, 7);
                            var day = e.timestamp.slice(8, 10);
                            var hour = parseInt(e.timestamp.slice(11, 13)) + 1;
                            var minutes = e.timestamp.slice(14, 16);
                        }
                        else {
                            var year = month = day = hour = minutes = ''
                        }
                        //console.log(year, month, day, time, day+'.'+month+'.'+year+' '+time);
                        //{% for t in e.sentence.token.all %}{% if t.position >= e.position|minus:5 and t.position <= e.position|add:5 %}{{ t.word_form }} {% endif %}{% endfor %}
                        //
                        var new_row = '<tr name="record_of_'+record_type+'" class=\'clickable-row\' data-href="frame_'+e["position"]+'_'+e["id_of_sentence"]+'" title=\'Preview: ';

                        new_row += '\'>' +
                            '<td><a href="frame_'+e.position+'_'+e.id_of_sentence+'">'+e.verb_lemma+e.verb_addition+'</a></td>' +
                            '<td><a href="frame_'+e.position+'_'+e.id_of_sentence+'">'+e.id_of_sentence+'</a></td>' +
                            '<td><a href="frame_'+e.position+'_'+e.id_of_sentence+'">'+e.f_type+'</a></td> ' +
                            '<td><a href="frame_'+e.position+'_'+e.id_of_sentence+'">';
                            if (e.certainty === 1) {
                                new_row += '<span class="certainty_1">&#x2460;</span>'
                            }
                            else if (e.certainty === 2) {
                                new_row += '<span class="certainty_2">&#x2461;</span>'
                            }
                            else if (e.certainty === 3) {
                                new_row += '<span class="certainty_3">&#x2462;</span>'
                            }
                            else if (e.certainty === 4) {
                                new_row += '<span class="certainty_4">&#x2463;</span>'
                            }
                            else if (e.certainty === 5) {
                                new_row += '<span class="certainty_5">&#x2464;</span>'
                            }
                            new_row += '</a> </td> <td> <a href="frame_'+e.position+'_'+e.id_of_sentence+'">' + day+'.'+month+'.'+year+' '+hour+':'+minutes+ '</a> </td> </tr>';

                        parent_of_rows.append(new_row);
                    }
                /*var new_row = '<tr></tr><td  class="col-md-4"><a href="frame_'+e.position+'_'+e.sentence_id+'">'+e.verb_lemma+e.verb_addition+'</a></td>' +
                            '<td class="col-md-8"><a href="frame_'+e.position+'_'+e.sentence_id+'">'+e.f_type+'</a></td></tr>';
                        */
                }

                else {
                    for (var i = 0; i < data.length; i++){
                        var e = data[i].fields;
                        var new_row = '<tr name="record_of_not_annotated_frames" class=\'clickable-row\' data-href="frame_'+e.position+'_'+e.sentence_id+'">' +
                            '<td  class="col-md-4"><a href="frame_'+e.position+'_'+e.sentence_id+'">'+e.verb_lemma+e.verb_addition+'</a></td>' +
                            '<td class="col-md-8"><a href="frame_'+e.position+'_'+e.sentence_id+'">'+e.f_type+'</a></td></tr>';

                        parent_of_rows.append(new_row);
                    }
                }

                if (value === '' || value === undefined) {
                    var searchbox = $("#searchbox_"+record_type+"_"+kind_change);
                    searchbox.val("");
                }

                $("#nr_selection_"+record_type).html(data.length);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            //swal("Error", "Error: " + errorThrown + "\nStatus: " + textStatus + "\njqXHR: " + JSON.stringify(jqXHR), "error")
            /*swal("Error: " + errorThrown
                + "\nStatus: " + textStatus
                + "\njqXHR: " + JSON.stringify(jqXHR)
            );*/
            swal("Error. Please contact the system operator.");
        },
        complete: function (jqXHR, textStatus) {
        }

    });
}

