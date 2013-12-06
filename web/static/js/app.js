var app = angular.module("club", ["ui.keypress", "ngSanitize"]);

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback, error) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
        success: function(response) {
            if (typeof(callback) == "function") {
                callback(response);
            };
        },
        error: function(jqXHR, textStatus, errorThrown) {
            if (typeof(error) == "function") {
                error(jqXHR, textStatus);
            };
    }});
};

app.days = {'V': 0, 'S':1, 'D':2, 'L':3};

// var padId = $('#wikipad').attr('padId');
// $('#wikipad').pad({'padId':padId,
//                    'showChat':'false',
//                    'host':window.location.protocol + "//" + window.location.hostname+":9001",
//                    'userName': eventer.name,
//                    });
