'use strict';

(function() {
  getDependencies();

  function getDependencies() {
    var depList = ["ui.router", "oide.acemodes", "ui.bootstrap", "oide.editor", "oide.filebrowser", "oide.terminal"];
    var oide = getOideModule(depList);

    angular.element(document).ready(function() {
      angular.bootstrap(document, ['oide']);
    });
  }
}());
