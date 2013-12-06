var app = angular.module('club').
    controller('HomeController', ['$scope', function($scope) {
    }]).
    controller('MembersController', ['$scope', 'callbacks', function ($scope, callbacks) {
        $scope.members = eventer.init.members;

        callbacks.UpdateUser = function(obj) {
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
    }]).
    controller('PresenceController', ['$scope', 'days', function ($scope, days) {
        $scope.presence = eventer.init.presence;
        $scope.changed = false;

        $scope.select = function($presence) {
            var value = ($presence[1]+1)%3;
            var day = $presence[0];
            var index = days[day];
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
        };
    }]).
    controller('ChatController', ['$scope', 'callbacks', function ($scope, callbacks) {
        $scope.messages = [];
        $scope.chatVisible = false;
        $scope.toggle = function () {
            $scope.chatVisible ^= true;
        };
        $scope.sendChat = function($event) {
            if ($event) {
                $event.preventDefault();
            }
            // Don't send empty message
            if ($scope.chatMessage) {
                jQuery.postJSON(eventer.home+"/chat", {'message':$scope.chatMessage});
            }
            $scope.chatMessage = "";
        };
        callbacks.ChatMessage = function(message) {
            $scope.$apply(function() {
                $scope.messages.push(message);
                var el = $("#chat .chatMessages");
                el.animate({scrollTop: el.height()}, 'slow');;
            });
        };
    }]).
    controller('MessageController', ['$scope', 'callbacks', function($scope, callbacks) {
        callbacks.MessageThread = function(thread) {
            $scope.$apply(function() {
                $scope.threads.push(thread);
            });
        };
        callbacks.MessageReply = function(threadUpdate) {
            $scope.$apply(function() {
                for (var index in $scope.threads) {
                    var thread = $scope.threads[index];
                    if (threadUpdate.threadId == thread.threadId) {
                        thread.push(threadUpdate.comment);
                        thread.updated = true;
                        break;
                    };
                };
            });
        };
    }]).
    controller('NewMessageController', ['$scope', function($scope) {
        var getEmptyMessage = function () {
            return {title: '', comment: ''};
        }
        $scope.comment = getEmptyMessage();
        $scope.sendMessage = function() {
            jQuery.postJSON(eventer.home+"/message/new", {'message':$scope.comment});
            $scope.comment = getEmptyMessage();
        };
    }]);
