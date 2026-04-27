import express from "express";
import cors from "cors";
import clickRouter from "./routes";

const app = express();
app.use(cors());
app.use(express.json());

app.use("/api", clickRouter);

const PORT = 3005;
app.listen(PORT, () => {
    console.log(`🚀 Central API running on http://localhost:${PORT}/api`);
});