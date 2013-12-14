var app = angular.module('club').
    controller('HomeController', ['$scope', function($scope) {
    }]).
    controller('DisplayController', ['$scope', '$rootScope', '$compile', function($scope, $rootScope, $compile) {
        $scope.remove = function () {
            $scope.visible = false;
            $("#display-panel").html("");
        }
        $rootScope.$on("displayContent", function (event, content) {
            var menu = $compile('<div class="display-menu" display-menu></div>')($scope);
            content.prepend(menu);
            content.resizable({handles: "all"});
            content.draggable({distance: 5, containment: "document", handle: ".drag-handle"});
            $("#display-panel").html("");
            $("#display-panel").append(content);
            $scope.visible=true;
        });
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
                presence: $scope.presence.map(function(m) {
                    if (typeof m[1] == "number") {
                        return m[1];
                    }
                    else {
                        return -1;
                    }
                })
            };
            jQuery.postJSON(eventer.home+"/user/presence", data);
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
                var elWindow = $("#chat .chatWindow");
                el.animate({scrollTop: elWindow.height()}, 'slow');;
            });
        };
    }]).
    controller('MessageController', ['$scope', '$rootScope', '$http', '$compile', 'callbacks', function($scope, $rootScope, $http, $compile, callbacks) {
        $scope.threads = eventer.init.messages;
        $scope.displayScope = null;

        /** Show a message in the display panel. */
        $scope.display = function (thread) {

            thread.updated = false;
            thread.newClass = "";
            thread.newComments = 0;

            $http({method: 'GET', url: eventer.home + "/message/view/" + thread.id}).
                success(function(data, status, headers, config) {
                    var scope = $rootScope.$new(true);
                    scope.thread = data;
                    $scope.displayScope = scope;
                    scope.sendReply = function() {
                        var data = { thread_id: thread.id, reply: scope.thread.reply };
                        jQuery.postJSON(eventer.home+"/message/reply", data);
                        scope.thread.reply="";
                    }

                    

                    var content = $compile("<div display-thread></div>")(scope);

                    // Arrange position
                    var targetOffset = $("#thread-list").offset();
                    var rootOffset = $("#main").offset();
                    var x = targetOffset.left-rootOffset.left;
                    var y = targetOffset.top-rootOffset.top;

                    $rootScope.$emit("displayContent", content);
                    content.offset({left: x, top: y});
                    content.width($("#thread-list").width()-22);
                });
        };

        /** Update of a new thread. */
        callbacks.NewThread = function(thread) {
            $scope.$apply(function() {
                $scope.threads.unshift(thread);
            });
        };
        /** Update: new reply. */
        callbacks.ThreadReply = function(threadUpdate) {
            $scope.$apply(function() {
                for (var index in $scope.threads) {
                    var thread = $scope.threads[index];
                    if (threadUpdate.threadId == thread.threadId) {
                        thread.newComments = (thread.newComments ||0)+ 1;
                        thread.newClass = "new";
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
            jQuery.postJSON(eventer.home+"/message/new", $scope.comment);
            $scope.comment = getEmptyMessage();
        };
    }]);
