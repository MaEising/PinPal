function update_quantity(id) {
  console.log("Button id:", id);

  let gameId = id.split("-")[0];
  let action = id.split("-")[3];
  let penaltyId = id.split("-")[1];
  let participantId = id.split("-")[2];

  let targetId =
    gameId + "-" + penaltyId + "-" + participantId + "-penalty-quantity";
  let targetElement = document.getElementById(targetId);
  let new_quantity;

  let xhr = new XMLHttpRequest();
  xhr.open("POST", "/update_quantity", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
      let currentValue = parseInt(targetElement.innerHTML, 10);
      if (action === "add") {
        if (currentValue + 1 >= 0) {
          targetElement.innerHTML = currentValue + 1;
          new_quantity = currentValue + 1;
        }
      } else if (action === "subtract") {
        if (currentValue - 1 >= 0) {
          targetElement.innerHTML = currentValue - 1;
          new_quantity = currentValue - 1;
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
