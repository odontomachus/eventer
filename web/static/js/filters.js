angular.module('club').
    /**
     * Truncate Filter
     * @Param text
     * @Param length, default is 40
     * @Param end, default is "..."
     * @return string
     */
    filter('truncate', function () {
        return function (text, length, end) {
            if (!text) {
                return "";
            }
            if (isNaN(length))
                length = 40;

            if (end === undefined)
                end = "...";

            if (text.length <= length) {
                return text;
            }
            else {
                // Try and split on a word boundary
                var pattern = new RegExp("^([.]{3,$len})\b.*$".replace("$len", length-end.length));
                return String(text).replace(pattern, "$1").substring(0, length-end.length) + end;
            }

        };
    });
