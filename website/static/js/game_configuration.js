// Function to remove non-numeric characters from a string
function removeNonNumeric(inputString) {
  return inputString.replace(/[^0-9.]/g, "");
}

// Function to update the quantity and total fine
function updateQuantity(id) {
  const [
    gameId,
    penaltyId,
    participantId,
    payAmount,
    action,
    isInvert,
    allParticipants,
  ] = id.split("-");
  console.log(id.split("-"))
  const targetId = `${gameId}-${penaltyId}-${participantId}-${payAmount}-penalty-quantity`; // Field displaying the quantity for a penalty. One for each penalty for each participant
  const targetElement = document.getElementById(targetId);

  // Function to handle add and subtract actions
  function handleQuantity(element) {
    const currentValue = parseInt(element.innerHTML, 10);

    if (action === "add" && currentValue + 1 >= 0) {
      element.innerHTML = currentValue + 1;
    } else if (action === "subtract" && currentValue - 1 >= 0) {
      element.innerHTML = currentValue - 1;
    }
  }
  // Penalty is inverted -> everyone except the Participant who got the penalty should receive a totalFine update, the calling participant only gets quantity increase
  if (isInvert && allParticipants) {
    // Update quantity for the callingParticipant
    handleQuantity(targetElement);
    
// Get all total fine elements of all participants except the calling participant
    const totalFineElementsToUpdate = [];
    JSON.parse(allParticipants).forEach((id => {
      console.log("Update for all participants",id);
      if (id != participantId) {
        const selector = `${gameId}-${id}-total-fine`;
        const element = document.getElementById(selector);
        
      if (element) {
        totalFineElementsToUpdate.push(element);
        console.log("TotalFineElements",totalFineElementsToUpdate)
      }
    }
    }));

// Update total fine elements for all participants except the calling participant
    totalFineElementsToUpdate.forEach((element) => {
        const currentTotalFine = parseFloat(
          removeNonNumeric(element.innerHTML)
        );
        if (action === "add") {
          element.innerHTML = `${(
            currentTotalFine + parseFloat(payAmount)
          ).toFixed(2)}€`;
        } else if (action === "subtract") {
          element.innerHTML = `${(
            currentTotalFine - parseFloat(payAmount)
          ).toFixed(2)}€`;
        }
    });
  // Penalty is not inverted -> calling participant gets quantity increase and his totalFine increased
  } else {
    handleQuantity(targetElement);
    const currParticipantTotalFineId = `${gameId}-${participantId}-total-fine`; // Id of the totalFine field 
    const currPartTotalFine = document.getElementById(currParticipantTotalFineId);
    const currPartTotalFineValue = parseFloat(removeNonNumeric(currPartTotalFine.innerHTML))
    if (action === "add") {
      currPartTotalFine.innerHTML = `${(currPartTotalFineValue + parseFloat(payAmount)).toFixed(2)}€`;
    } else if (action === "subtract") {
      currPartTotalFine.innerHTML = `${(currPartTotalFineValue - parseFloat(payAmount)).toFixed(2)}€`;
    }
  }

  // Make the AJAX request
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/update_quantity", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
      // Handle AJAX response if needed
    }
  };
  xhr.send(
    JSON.stringify({
      penaltyId,
      participantId,
      action,
      game_id: gameId,
    })
  );
}



let currentRow = null;
// Function to toggle the display of user penalties
function toggleUserPenalties(tableCellId) {
  if (currentRow !== null && currentRow[0].id === tableCellId) {
    currentRow.forEach((cell) => cell.classList.add("hideRow"));
    currentRow = null;
  } else {
    displayUserPenalties(tableCellId);
  }
}

// Function to display user penalties
function displayUserPenalties(tableCellId) {
  if (currentRow !== null) {
    currentRow.forEach((cell) => cell.classList.add("hideRow"));
  }

  const tableCells = document.querySelectorAll(`[id='${tableCellId}']`);
  tableCells.forEach((cell) => cell.classList.remove("hideRow"));
  currentRow = tableCells;
}
