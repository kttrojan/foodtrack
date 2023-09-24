// BASED ON:
// https://stackoverflow.com/questions/35955504/add-table-row-button-on-click


function addField(table) {
    var tableRef = document.getElementById(table);
    var newRow = tableRef.insertRow(-1);

    var newCell = newRow.insertCell(0);
    var newElem = document.createElement('input');
    newElem.setAttribute("name", "ingredient[]");
    newElem.setAttribute("type", "text");
    newElem.setAttribute("placeholder", "Ingredient");
    newElem.setAttribute("class", "form-control mx-auto w-auto");
    newElem.setAttribute("autocomplete", "off")
    newCell.appendChild(newElem);

    newCell = newRow.insertCell(1);
    newElem = document.createElement('input');
    newElem.setAttribute("name", "quantity[]"); // Fix name attribute
    newElem.setAttribute("type", "text");
    newElem.setAttribute("placeholder", "1");
    newElem.setAttribute("class", "form-control mx-auto w-auto");
    newCell.appendChild(newElem);

    newCell = newRow.insertCell(2);
    var selectElem = document.createElement('select');
    selectElem.setAttribute("name", "unit[]"); // Fix name attribute
    selectElem.setAttribute("class", "form-control mx-auto w-auto");

    var unitOptions = ["--Choose unit--", "pcs", "gram [g]", "kilogram [kg]", "liter [l]", "mililiter [ml]", "centimeter [cm]", "teaspoon [tsp]", "tablespoon [tbsp]", "cup [c]"];
    var unitAbbr = ["", "pcs", "g", "kg", "l", "ml", "cm", "tsp", "tbsp", "cups"];

    for (var i = 0; i < unitOptions.length; i++) {
        var optionElem = document.createElement('option');
        optionElem.value = unitAbbr[i];
        optionElem.text = unitOptions[i];
        selectElem.appendChild(optionElem);
    }

    newCell.appendChild(selectElem);

    newCell = newRow.insertCell(3);
    var newButton = document.createElement('input');
    newButton.setAttribute("type", "button");
    newButton.setAttribute("value", "Remove");
    newButton.setAttribute("class", "btn btn-primary");
    newCell.appendChild(newButton);

    // Attach the event handler to the new "Remove" button
    newButton.addEventListener('click', function () {
        deleteRow(this);
    });
}

window.deleteRow = function deleteRow(o) {
    var p = o.parentNode.parentNode;
    p.parentNode.removeChild(p);
}