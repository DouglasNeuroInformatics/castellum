$(function() {
  var disableInput = function(event) {
    var $nocomment = $(event.target);
    var $target = $('#' + $nocomment.data('target'));
    $target.prop('disabled', $nocomment.prop('checked'));
  };

  $(document).on('change', '[data-js="no-comment"]', disableInput);

  $('[data-js="no-comment"]').each(function(i, element) {
  	disableInput({target: element});
  });
});