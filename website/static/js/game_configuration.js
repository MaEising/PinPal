function update_quantity(id) {
  console.log("Button id:", id);
  let gameId = id.split("-")[0];
  let penaltyId = id.split("-")[1];
  let participantId = id.split("-")[2];
  let payAmount = id.split("-")[3];
  let action = id.split("-")[4];

  let targetId =
    gameId + "-" + penaltyId + "-" + participantId + "-" + payAmount + "-penalty-quantity";
  let targetElement = document.getElementById(targetId);

  let totalFineId = gameId + "-" + participantId + "-total-fine";
  console.log("TotalFineId:", totalFineId)
  let totalFineElement = document.getElementById(totalFineId);

  let xhr = new XMLHttpRequest();
  xhr.open("POST", "/update_quantity", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
      let currentValue = parseInt(targetElement.innerHTML, 10);
      let currentTotalFine = parseInt(totalFineElement.innerHTML, 10);
      if (action === "add") {
        if (currentValue + 1 >= 0) {
          targetElement.innerHTML = currentValue + 1;
          totalFineElement.innerHTML = currentTotalFine + payAmount;
        }
      } else if (action === "subtract") {
        if (currentValue - 1 >= 0) {
          targetElement.innerHTML = currentValue - 1;
          totalFineElement.innerHTML = currentTotalFine - payAmount;
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
