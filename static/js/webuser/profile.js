$(function () {
    $(".member-row").click(function () {
        $(this).next().toggle()
    });
});

$(window).resize(function() {
    ChangeWidth();
});

function ChangeWidth() {
  if($( window ).width() < 750){
    $(".share-table-div").css({"width": $( window ).width()-50 });
  }
  else{
    $(".share-table-div").css({"width": "100%" });
  }
  //alert($( window ).width());
}

window.onload = ChangeWidth