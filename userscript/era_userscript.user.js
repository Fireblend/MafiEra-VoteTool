// ==UserScript==
// @name        MafiEraVoteTool
// @version     0.2
// @namespace   http://www.fireblend.com/
// @updateURL   https://openuserjs.org/meta/Fireblend/era_userscript.meta.js
// @downloadURL https://openuserjs.org/src/scripts/Fireblend/era_userscript.user.js
// @license     MIT
// @icon        https://cdn.discordapp.com/icons/161525734102401024/d15bc9248dcbe0d35dbbba1fa096c348.png
// @homepageURL http://www.fireblend.com/
// @author      Sergio Morales
// @description The MafiEra Vote Tool, made easier!
// @include     http*://www.resetera.com/threads/*
// @include     http*://www.resetera.com/threads/*/*
// @require     https://code.jquery.com/ui/1.12.1/jquery-ui.js
// @require     http://code.jquery.com/ui/1.11.4/jquery-ui.js
// @resource    customCSS https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css
// @run-at      document-idle
// @grant       GM_addStyle
// @grant       GM_getResourceText
// ==/UserScript==

(function () {
  'use strict';

  function addButton() {
    var buttonLocations = document.querySelectorAll('fieldset.breadcrumb');
    var a = makeButton();
    buttonLocations[0].appendChild(a);
    var b = makeButton();
    buttonLocations[2].appendChild(b);
    for (var location in buttonLocations) {}
  }

  function openDialog() {
    var url = window.location.href;
    var page = "https://vote.fireblend.com/" + url.split("/threads/")[1].split("/")[0] + "/simple";

    var $dialog = $('<div></div>')
      .html('<iframe id="myDialog" style="background-color: #ffffff; border: 0px; " src="' + page + '" width="100%" height="100%"></iframe>')
      .dialog({
        autoOpen: false,
        modal: true,
        height: 700,
        width: 500,
        title: "MafiEra Vote Count",
        resizable: false
      });
    $dialog.dialog('open');
  }

  function makeButton() {
    var a = document.createElement('span');
    var url = window.location.href;
    a.setAttribute('style', 'cursor:pointer;');
    a.setAttribute('class', "crumb bottomLink videob");
    a.addEventListener("click", openDialog, false);
    a.setAttribute('target', '_blank');
    a.appendChild(document.createTextNode("Vote Count"));
    return a;
  }
  var newCSS = GM_getResourceText("customCSS");
  GM_addStyle(newCSS);
  GM_addStyle('.ui-dialog .ui-dialog-content { overflow: hidden; }');
  addButton();
})();
