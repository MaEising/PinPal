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

  const targetId = `${gameId}-${penaltyId}-${participantId}-${payAmount}-penalty-quantity`;
  const targetElement = document.getElementById(targetId);
  const totalFineElements = document.querySelectorAll(`[id$="-total-fine"]`);

  // Function to handle add and subtract actions
  function handleAction(element, amount) {
    const currentValue = parseInt(element.innerHTML, 10);

    if (action === "add" && currentValue + 1 >= 0) {
      element.innerHTML = currentValue + 1;
    } else if (action === "subtract" && currentValue - 1 >= 0) {
      element.innerHTML = currentValue - 1;
    }
  }

  if (isInvert && allParticipants) {
    // XXX If this is inverted the handleAction must be called for each participant (except the participant who invoked updateQuantity). Each time targetElement has to be adjusted with the new ParticipantId
    handleAction(targetElement, parseFloat(payAmount));

    // Update total fine elements for all participants except the current participant
    totalFineElements.forEach((element) => {
      const elementId = element.getAttribute("id");
      const currentParticipantTotalFineId = `${gameId}-${participantId}-total-fine`;

      if (elementId === currentParticipantTotalFineId) {
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
      }
    });
  } else {
    handleAction(targetElement, parseFloat(payAmount));
    const currentParticipantTotalFineId = `${gameId}-${participantId}-total-fine`;
    if (action === "add") {
      element.innerHTML = `${(currentTotalFine + parseFloat(payAmount)).toFixed(
        2
      )}€`;
    } else if (action === "subtract") {
      element.innerHTML = `${(currentTotalFine - parseFloat(payAmount)).toFixed(
        2
      )}€`;
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
