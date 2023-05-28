let currentRow = null;
function stripNonNumeric(inputString) {
  return inputString.replace(/[^0-9.]/g, "");
}
function update_quantity(id) {
  console.log("Button id:", id);
  let gameId = id.split("-")[0];
  let penaltyId = id.split("-")[1];
  let participantId = id.split("-")[2];
  let payAmount = id.split("-")[3];
  let action = id.split("-")[4];
  console.log("Pay amount:", payAmount);

  let targetId =
    gameId +
    "-" +
    penaltyId +
    "-" +
    participantId +
    "-" +
    payAmount +
    "-penalty-quantity";
  let targetElement = document.getElementById(targetId);

  let totalFineId = gameId + "-" + participantId + "-total-fine";
  console.log("TotalFineId:", totalFineId);
  let totalFineElement = document.getElementById(totalFineId);

  let xhr = new XMLHttpRequest();
  xhr.open("POST", "/update_quantity", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
      let currentValue = parseInt(targetElement.innerHTML, 10);
      let currentTotalFine = parseFloat(
        stripNonNumeric(totalFineElement.innerHTML, 10)
      );
      if (action === "add") {
        if (currentValue + 1 >= 0) {
          targetElement.innerHTML = currentValue + 1;
          totalFineElement.innerHTML =
            (currentTotalFine + parseFloat(payAmount)).toFixed(2) + "€";
        }
      } else if (action === "subtract") {
        if (currentValue - 1 >= 0) {
          targetElement.innerHTML = currentValue - 1;
          totalFineElement.innerHTML =
            (currentTotalFine - parseFloat(payAmount)).toFixed(2) + "€";
        }
      }
    }
  };
  xhr.send(
    JSON.stringify({
      penaltyId: penaltyId,
      participantId: participantId,
      action: action,
      game_id: gameId,
    })
  );
}

function toggleUserPenalties(tableCellId) {
  // Check if the clicked row is already revealed
  if (currentRow !== null && currentRow[0].id === tableCellId) {
    // Hide the currently revealed row
    currentRow.forEach(function (cell) {
      cell.classList.add("hideRow");
    });
    currentRow = null;
  } else {
    displayUserPenalties(tableCellId);
  }
}
// Retrieves an id that includes an identifier for all table cells inside a row. On each <td> there is a class set "hideRow" which has to be removed on function call.
// If a different row is targeted hideRow should be added back again
// id looks like this {{ player_record.game_id}}-{{ player_record.participant_id }}-tablecell
function displayUserPenalties(tableCellId) {
  var tableCells = document.querySelectorAll("[id='" + tableCellId + "']");
  // check if row is currently revealed
  if (currentRow !== null) {
    // Hide the currently revealed row
    currentRow.forEach(function (cell) {
      cell.classList.add("hideRow");
    });
  }
  // Remove "hideRow" class from all table cells with the specified id
  tableCells.forEach(function (cell) {
    cell.classList.remove("hideRow");
  });
  currentRow = tableCells;
}
