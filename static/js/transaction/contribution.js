


function ChangeAmount() {
  cp = document.getElementById("contribution_period");
  amount = document.getElementById("amount");
  amount.value = 25*GetSelectValues(cp).length;
}


function ChangeContPeriodSelectList(){
  var contSelect = document.getElementById("contribution_period");

  var shareSelect = document.getElementById("share");
  var selectedShareId = shareSelect.options[shareSelect.selectedIndex].value;

  var is_there_old = document.getElementById("is_there_old");
  var contPeriodList;
  if(is_there_old.checked == true) {
    contPeriodList = all_periods_of[selectedShareId];
  } else {
    contPeriodList = periods_of[selectedShareId];
  }

  ChangeSelectList(contSelect, contPeriodList, "Ödenmemiş aidatınız bulunamadı...");
}


$(function () {
  var cp = document.getElementById("contribution_period")
  cp.onchange = ChangeAmount;

  var share_select = document.getElementById("share");
  share_select.onchange = ChangeContPeriodSelectList;
});


function ChangeToMultiplePeriod() {
  var checkBox = document.getElementById("is_multiple_period");
  if (checkBox.checked == true){
    document.getElementById('contribution_period').setAttribute("multiple","");
  }
  else {
    document.getElementById('contribution_period').removeAttribute("multiple","");
  }
}


function AddCheckBox() {
  var check_boxes = CreateHtmlElement('<p style="text-align: center;">Old contribution: <input type="checkbox" id="is_there_old" onclick="ChangeContPeriodSelectList()"><br>Multiple contribution: <input type="checkbox" id="is_multiple_period" onclick="ChangeToMultiplePeriod()"></p>');

  var cp_select = document.getElementById('contribution_period');
  cp_select.parentNode.insertBefore(check_boxes, cp_select.nextSibling);
}


$(document).ready(function() {
  AddCheckBox();
  ChangeToMultiplePeriod();
  ChangeContPeriodSelectList();

});
