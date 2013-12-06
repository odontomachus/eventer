var app = angular.module("club", ["ui.keypress", "ngSanitize"]).
    constant('days', {'V': 0, 'S':1, 'D':2, 'L':3}).
    value('callbacks', {}).
    run(function (callbacks) {
        // Setup etherpad
        // var padId = $('#wikipad').attr('padId');
        // $('#wikipad').pad({'padId':padId,
        //                    'showChat':'false',
        //                    'host':window.location.protocol + "//" + window.location.hostname+":9001",
        //                    'userName': eventer.name,
        //                    });

        // Setup back-end updates channel
        var getWs = function(timeout) {
            var innerWs = new WebSocket("ws://"+window.location.hostname+eventer.home+"/updates");
            innerWs.onmessage = function(evt) {
	        var data = $.parseJSON(evt.data);
	        for(var dataKey in data) {
                    var callback = callbacks[dataKey]
                    var obj = data[dataKey];
                    if (callback) {
                        callback(obj);
                    };
	        };
            };
            innerWs.onclose = function (evt) {
                var nextTimeout = Math.min(timeout*1.2 + 5, 3000);
                setTimeout(function () {
                    ws = getWs(nextTimeout);
                }, timeout*1000);
            }
            /**
               Set connection retry timeout to a low value upon a successful connection.
            */
            innerWs.onopen = function (evt) {
                setTimeout(function () {
                    if (innerWs.readyState == WebSocket.OPEN) {
                        timeout = 1;
                        innerWs.onclose = function (evt) {
                            var nextTimeout = Math.min(timeout*1.2 + 5, 3000);
                            setTimeout(function () {
                                ws = getWs(nextTimeout);
                            }, timeout*1000);
                        };
                    };
                });
            };
            return innerWs;
        };
        var ws = getWs();
    });

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

