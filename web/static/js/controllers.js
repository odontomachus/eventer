var app = angular.module('club')
    .controller('home', [function () {
        var ws = new WebSocket("ws://"+window.location.hostname+eventer.home+"/updates");
        ws.onmessage = function(evt) {
	    var data = $.parseJSON(evt.data);
	    for(var dataKey in data) {
                var callback = eventer.callbacks[dataKey]
                var obj = data[dataKey];
                if (callback) {
                    callback(obj);
                };
	    };
        };
}]);

function MembersController($scope) {
    $scope.members = eventer.init.members;

    eventer.callbacks.UpdateUser = function(obj) {
        $scope.$apply(function() {
            for (var key in $scope.members) {
                console.log($scope);
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
        var index = eventer.days[day];
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
    eventer.callbacks.ChatMessage = function(message) {
        $scope.$apply(function() {
            $scope.messages.push(message);
            var el = $("#chat .chatMessages");
            el.animate({scrollTop: el.height()}, 'slow');;
        });
    };
};
