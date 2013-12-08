angular.module("club").
    directive("displayThread", function () {
        return {
            restrict: 'E',
            template :
            '<div class="thread-content">' +
                '<div class="header">' +
                '<div class="title">{{thread.title}}</div>' +
                '<div class="user">{{thread.user.name}}</div>' +
                '</div>' +
                '<div class="body">{{thread.comment}}</div>' +
                '</div>',
        };
    });
