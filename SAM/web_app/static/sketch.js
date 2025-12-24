let input;

function setup() {
  createCanvas(400, 400);
  input = createInput();
  input.position(20, 20);
  input.size(200);

  input.changed(sendText); // triggered when Enter is pressed
}

function draw() {
  background(220);
}

function fetchData() {
  fetch("/data")
    .then(res => res.json())
    .then(data => {
      counter = data.counter;
      setTimeout(fetchData, 1000);
    });
}

function sendText() {
  let value = input.value();

  fetch("/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: value })
  })
    .then(res => res.json())
    .then(data => {
      console.log("Server received:", data.received);
      input.value(""); // clear input
    });
}