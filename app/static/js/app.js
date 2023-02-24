
$(document).ready(function(){

    $(this).on('click',function(){
        $(".input-field").removeClass("invalid");
    });

    (function(){
        setTimeout(function(){$('.alert').fadeOut("fast");}, 8000);
    })();

});