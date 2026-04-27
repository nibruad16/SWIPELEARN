import { Router } from "express";
import { getAllClicks, incrementClick } from "./services";

const router = Router();

router.get("/clicks", async (req, res) => {
    const data = await getAllClicks();
    res.json(data);
});

router.post("/clicks", async (req, res) => {
    const { appName } = req.body;
    try {
        await incrementClick(appName);
        res.json({ success: true });
    } catch (e) {
        res.status(400).json({ error: (e as Error).message });
    }
});

export default router;