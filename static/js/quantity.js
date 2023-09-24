function getQuantity(item) {
  // Prompt the user for a quantity
  let quantity = prompt("Enter ingredient's quantity", 1);

  // Check if the user clicked 'Cancel' or entered an empty value
  if (quantity === null || quantity.trim() === "") {
    event.preventDefault();
    return;
  }

  // Update the quantity element's value
  let element = document.getElementById("ing_quant_" + item);
  if (element) {
    element.setAttribute("value", quantity);
  }

  // Submit the form after a delay
  let form = document.getElementById("form_" + item);
  if (form) {
    setTimeout(function () {
      form.submit();
    }, 1000);
  }
}