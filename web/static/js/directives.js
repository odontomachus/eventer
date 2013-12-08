angular.module("club").
    directive("displayThread", function () {
        return {
            restrict: 'AE',
            template :
            '<div class="content">' +
                '<div class="thread-content">' +
                '<div class="header">' +
                '<div class="title">{{thread.title}}</div>' +
                '<div class="user">{{thread.user.name}}</div>' +
                '</div>' +
                '<div class="body">{{thread.comment}}</div>' +
                '</div>' +
                '</div>',
        };
    }).
    directive("displayMenu", function() {
        return {
            restrict: 'AE',
            transclude: true,
            template: '<div class="drag-handle ui-widget-header"><a class="btn-close" ng-click="remove()">&times;</a></div>',
        }
    });
            
           
