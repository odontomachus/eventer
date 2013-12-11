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
                '<div class="reply">'+
                '<a class="action" ng-click="thread.showReply=true">Répondre</a>' +
                '<div ng-show="thread.showReply">' +
                '<textarea ng-model="thread.reply">{{thread.reply}}</textarea>' +
                '<button ng-click="sendReply()">Envoyer</button>' +
                '</div>' +
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
            
           
