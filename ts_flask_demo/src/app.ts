import express from "express";
import userRouter from "./routes/user.routes";

const app = express();

app.use(express.json());
app.use("/api", userRouter);

app.listen(5001, () => {
  console.log("TS server running at http://127.0.0.1:5001");
});