$(document).ready(function() {
    start = new Date();
});

window.addEventListener("unload", logData, false);

/*function logData() {
    var end = new Date();
    console.log(end-start);
    navigator.sendBeacon("timespent", end-start, jQuery("[name=csrfmiddlewaretoken]").val());
}*/

function logData() {
    //console.log("leave", $("#frame_number").val(), document.getElementById("frame_number").value);
    var end = new Date();
    console.log(end - start);
    $.ajax({
        url: "timespent",
        method: "POST",
        async: false,
        data: {
            timeSpent: end - start,
            //frame_id: $("#frame_number").val(),
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
                console.log(data);
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
