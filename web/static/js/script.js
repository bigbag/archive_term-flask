var $popup;
var $body;
var $element = new Object();

var showPopup = function(){
	$element.showPopupButton = $(this);
	var popupId =  'popup-' + $(this).attr('id');
	$popup.removeClass('g-hide').attr('id', popupId).animate({opacity: 1}, 50, function(){
		$body.addClass('g-overflow-h');
	});
	return false;

};
var hidePopup = function(){
	if ($element.showPopupButton){
		$element.showPopupButton.removeClass('active');
		$popup.animate({opacity: 0}, 200, function(){
			$(this).addClass('g-hide');
			$body.removeClass('g-overflow-h');
		});
	}
	return false;
};
$(document).keydown(function(e){
	if(e.which == 27){
		$popup.hasClass('hide')||hidePopup();
	}
});
$(document).on('click','.popup',hidePopup);
$(document).on('click','.popup-window', function(event){
	event.stopPropagation();
});



$(window).load(function() {
	$popup = $('.popup');
	$body = $('body');

	$(document).on('click','.j-show-popup', showPopup);
	$(document).on('click','.close-popup', hidePopup);


	$(document).on('focus','.f-dd-input', function(){
		$(this).addClass('focus');
	});
	$(document).on('click','.dd-list li', function(){
		var listItem = $(this).html();
		$(this).parents('.f-dd-light').find('.f-dd-input')
								      .val(listItem)
									  .removeClass('focus');
	});
	$(document).on('click',function(){
		$('.f-dd-input').removeClass('focus');
	});
	$(document).on('click','.f-dd-light', function(event){
		event.stopPropagation();
	});

});