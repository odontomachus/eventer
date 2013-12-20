angular.module("club").
    directive("displayThread", function () {
        return {
            restrict: 'AE',
            template :
            '<div class="content">' +
              '<div class="thread-content">' +
	        '<div class="initial">' +
                  '<div class="header">' +
                    '<div class="title">{{thread.title}}</div>' +
                    '<div class="user">{{thread.user.name}}</div>' +
                  '</div>' +
                  '<div class="body">{{thread.comment | escapeHTML | newlines | linky }}</div>' +
                '</div>' +
                '<div class="reply" ng-repeat="reply in thread.replies">' +
                  '<div class="user">{{reply.user.name}}</div>' +
                  '<div class="body" ng-bind-html="reply.comment | escapeHTML| newlines| linky"></div>' +
                '</div>' +
                '<div class="do-reply">'+
                  '<a class="action" ng-click="thread.showReply=true">Répondre</a>' +
                  '<div ng-show="thread.showReply">' +
                  '<div class="compose-wrapper"><textarea class="compose" ng-model="thread.reply">{{thread.reply}}</textarea></div>' +
                    '<button ng-click="sendReply()">Envoyer</button>' +
                  '</div>' +
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
           
