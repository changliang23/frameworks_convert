import { Router, Request, Response } from "express";
import { userService } from "../services/user.service";
import { RegisterDTO, LoginDTO } from "../dto/user.dto";
import { ApiResult } from "../types/result";

const router = Router();

router.post("/register", (req: Request<{}, {}, RegisterDTO>, res: Response<ApiResult<null>>) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ code: 400, msg: "missing param" });
  }

  const ok = userService.register({ username, password });

  if (!ok) {
    return res.status(409).json({ code: 409, msg: "user exists" });
  }

  res.json({ code: 200, msg: "register success" });
});

router.post("/login", (req: Request<{}, {}, LoginDTO>, res: Response<ApiResult<null>>) => {
  const { username, password } = req.body;

  const ok = userService.login(username, password);
  if (!ok) {
    return res.status(401).json({ code: 401, msg: "login failed" });
  }

  res.json({ code: 200, msg: "login success" });
});

router.get("/users", (req, res: Response<ApiResult<string[]>>) => {
  const users = userService.list();
  res.json({ code: 200, msg: "ok", data: users });
});

router.delete("/users/:username", (req, res: Response<ApiResult<null>>) => {
  const ok = userService.delete(req.params.username);
  if (!ok) {
    return res.status(404).json({ code: 404, msg: "user not found" });
  }
  res.json({ code: 200, msg: "delete success" });
});

export default router;