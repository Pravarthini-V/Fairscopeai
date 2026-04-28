const express = require("express");
const app = express();

const port = process.env.PORT;

app.get("/", (req, res) => {
  res.send("FairscopeAI is running 🚀");
});

app.listen(port, "0.0.0.0", () => {
  console.log("Server running on port " + port);
});
