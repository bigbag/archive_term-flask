'use strict';

angular.module('term').service('contentService', function() {
    var resultModal = angular.element('.m-result');
    var resultContent = resultModal.find('p');

    //Вызываем модальное окно
    this.setModal = function(content, type){
        resultModal.removeClass('m-negative');
        if (type == 'error') {
            resultModal.addClass('m-negative');
        }
        resultModal.hide();
        resultModal.show();
        resultContent.text(content);
        setTimeout(function(){
          resultModal.hide();
        }, 5000);
      };

    var scroll_speed = 600;
    //Автоскролинг до нужного блока
    this.scrollPage = function(id, speed){
        speed = typeof speed !== 'undefined' ? speed : scroll_speed;
        var scroll_height = $(id).offset().top;
          $('html, body').animate({
            scrollTop: scroll_height
          }, speed);
      };
});

angular.module('term').service('dialogService', function() {
    var dialogDOM = angular.element("#dialog-confirm");
    var dialogQuestion = angular.element("#dialog-question");
    
    var yesNoDialog = function(callback, question) {
      dialogQuestion.html(question);
      dialogDOM.dialog({
        resizable: true,
        height:240,
        minHeight:240,
        minWidth: 380,
        modal: true,
        buttons: {
          'Да': function() {
            callback('yes');
            $( this ).dialog( "close" );
          },
          'Нет': function() {
            callback('no');
            $( this ).dialog( "close" );
          }
        }
      });    

    };

    return {
      yesNoDialog: yesNoDialog
    };

});    