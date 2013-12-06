var app = angular.module('club');
app.callbacks = {};

app.controller('home', [function () {
    var getWs = function(timeout) {
        var innerWs = new WebSocket("ws://"+window.location.hostname+eventer.home+"/updates");
        innerWs.onmessage = function(evt) {
	    var data = $.parseJSON(evt.data);
	    for(var dataKey in data) {
                var callback = app.callbacks[dataKey]
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
}]);

function MembersController($scope) {
    $scope.members = eventer.init.members;

    app.callbacks.UpdateUser = function(obj) {
        $scope.$apply(function() {
            for (var key in $scope.members) {
                var member = $scope.members[key];
                if (member.name == obj.name) {
                    $scope.members[key] = obj;
                    break;
                };
            };
        });
    };
};

function PresenceController($scope) {
    $scope.presence = eventer.init.presence;
    $scope.changed = false;

    $scope.select = function($presence) {
        var value = ($presence[1]+1)%3;
        var day = $presence[0];
        var index = app.days[day];
        $scope.presence[index][1] = value;
        $scope.changed = true;
    }

    $scope.confirm = function() {
        $scope.changed = false;
        var data = {
            callback: "presence",
            presence: $scope.presence.map(function(m) {
                if (typeof m[1] == "number") {
                        return m[1];
                }
                else {
                    return -1;
                }
            })
        };
        jQuery.postJSON(eventer.home+"/update", data);
    }
};


function ChatController($scope) {
    $scope.messages = [];
    $scope.chatVisible = false;
    $scope.toggle = function () {
        $scope.chatVisible ^= true;
    };
    $scope.sendChat = function() {
        // Don't send empty message
        if ($scope.chatMessage) {
            jQuery.postJSON(eventer.home+"/chat", {'message':$scope.chatMessage});
        }
        $scope.chatMessage = "";
    };
    app.callbacks.ChatMessage = function(message) {
        $scope.$apply(function() {
            $scope.messages.push(message);
            var el = $("#chat .chatMessages");
            el.animate({scrollTop: el.height()}, 'slow');;
        });
    };
};
