function ChangeSelectList(formSelect, newList, ifListEmpty){
  if (!formSelect) {
    return;
  }

  while(formSelect.options.length) {
    formSelect.remove(0);
  }

  if(newList) {
    if(newList.length){
      var i;
      for(i=0; i<newList.length; i++) {
        var share = new Option(newList[i][1], newList[i][0]);
        formSelect.options.add(share);
      }
    }
    else{
      var share = new Option(ifListEmpty, "");
      formSelect.options.add(share);
    }
  }
}

// Return an array of the selected option values
// select is an HTML select element
function GetSelectValues(select) {
  var result = [];
  var options = select && select.options;
  var opt;

  for (var i=0, iLen=options.length; i<iLen; i++) {
    opt = options[i];

    if (opt.selected) {
      result.push(opt.value || opt.text);
    }
  }
  return result;
}


function CreateHtmlElement(htmlStr) {
  var frag = document.createDocumentFragment(),
    temp = document.createElement('div');
  temp.innerHTML = htmlStr;
  while (temp.firstChild) {
    frag.appendChild(temp.firstChild);
  }
  return frag;
}