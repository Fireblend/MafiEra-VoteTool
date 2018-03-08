// ==UserScript==
// @name        MafiEraVoteTool
// @version     0.1
// @namespace   http://www.fireblend.com/
// @updateURL   https://openuserjs.org/meta/Fireblend/era_userscript.meta.js
// @downloadURL https://openuserjs.org/src/scripts/Fireblend/era_userscript.user.js
// @license     CC-BY-NC-SA-4.0; https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
// @icon        https://dl.dropboxusercontent.com/u/57161259/icons/cs-ohnoes-icon.png
// @homepageURL http://www.fireblend.com/
// @author      Sergio Morales
// @description The MafiEra Vote Tool, made easier!
// @include     http*://www.resetera.com/threads/*
// @include     http*://www.resetera.com/threads/*/*
// @require     http://code.jquery.com/jquery-1.10.2.js
// @require     http://code.jquery.com/ui/1.11.4/jquery-ui.js
// @run-at      document-idle
// ==/UserScript==


(function() {
    'use strict';

    function addButton() {
        var buttonLocations = document.querySelectorAll('fieldset.breadcrumb');
          var a = makeButton();
          buttonLocations[0].appendChild(a);
          var b = makeButton();
          buttonLocations[2].appendChild(b);
        for (var location in buttonLocations){
        }
    }

function openDialog() {
    var url = window.location.href;
    var page = "https://vote.fireblend.com/"+url.split("/threads/")[1].split("/")[0];

    var $dialog = $('<div></div>')
    .html('<iframe style="border: 0px; " src="' + page + '" width="100%" height="100%"></iframe>')
    .dialog({
        autoOpen: false,
        modal: true,
        height: 625,
        width: 900
    });
    $dialog.dialog('open');
}

    function makeButton() {
        var a = document.createElement('a');
        var url = window.location.href;
        a.setAttribute('href', "javascript:openDialog()");
        a.setAttribute('class', "crumb bottomLink videob");
        a.addEventListener("click", openDialog, false);


        a.setAttribute('target', '_blank');
        a.appendChild(document.createTextNode("Vote Count"));
        return a;
    }
    addButton();
})();
