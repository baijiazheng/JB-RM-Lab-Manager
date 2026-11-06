# RM 战队实验室管理后台

> FastAPI + SQLite + Vue3 + Element Plus + JWT
> 内网部署，B/S 架构，前后端完全分离

---

## 📚 文档索引（先看哪个）

| 文档 | 谁看 | 内容 |
|---|---|---|
| **`docs/01-使用手册.md`** | **所有队员** | 怎么登录、看任务、提交 |
| **`docs/02-管理员手册.md`** | **管理员/组长** | 建用户、发任务、审核 |
| **`docs/03-部署手册.md`** | **维护者** | 部署到内网服务器 + PostgreSQL + 备份 |
| **`docs/04-二次开发指南.md`** | **要加功能的人** | 新增模块的完整代码模板 |
| **`docs/05-30人扩展路线.md`** | **队长** | ★ 从 MVP 到 30 人可用的升级路径 |
| **`docs/06-注意事项与坑.md`** | **所有人（尤其是 AI 会话）** | ★ 坑库 + 现状 + 待改进 |

**★★ 新会话接手：先读 `docs/06-注意事项与坑.md` 第零节。**

---

## 一、项目结构

```
JB-RM-Lab-Manager/
├── backend/                  # 后端（FastAPI）
│   ├── app/
│   │   ├── main.py           # ★ 入口（只做 3 件事：建 app / 挂中间件 / 挂路由）
│   │   ├── core/             # 基础设施
│   │   │   ├── config.py     # ★ 配置（改这里不改代码）
│   │   │   ├── database.py   # SQLAlchemy 连接
│   │   │   ├── security.py   # JWT + 密码哈希
│   │   │   ├── response.py   # 统一返回格式
│   │   │   ├── deps.py       # 依赖注入（当前用户 / 权限）
│   │   │   └── rate_limit.py # 登录限流
│   │   ├── models/           # 数据库模型
│   │   ├── schemas/          # Pydantic 校验
│   │   ├── api/              # ★ 路由（扩展点）
│   │   │   ├── __init__.py   # ★★★ 路由注册中心（唯一扩展点）
│   │   │   ├── auth.py       # 登录
│   │   │   ├── users.py      # 用户管理
│   │   │   └── tasks.py      # 任务 + 提交 + 附件
│   │   └── init_db.py        # 初始化数据库 + 管理员
│   ├── alembic/              # 数据库迁移
│   │   └── versions/0001_initial.py
│   ├── static/uploads/       # 附件存放
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # 前端（Vue3）
│   └── src/
│       ├── api/              # ★ 只做 HTTP，无业务逻辑
│       ├── router/           # 路由 + 守卫
│       ├── stores/           # Pinia（用户状态）
│       ├── layouts/          # 侧边栏 + 主内容区
│       └── views/            # 页面
└── README.md                 # 本文件
```

---

## 二、启动步骤

### 后端（先启动）

```bash
cd backend

# ① 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# ② 安装依赖
pip install -r requirements.txt

# ③ ⚠️ 重要：bcrypt 必须锁 4.0.1（4.1+ 和 passlib 1.7.4 不兼容）
pip install "bcrypt==4.0.1"

# ④ 初始化数据库 + 默认管理员
python -m app.init_db

# ⑤ 启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**验证：** 打开 http://127.0.0.1:8000/docs （Swagger 自动文档）

### 前端（再启动）

```bash
cd frontend

# ① 安装依赖
npm install

# ② 启动
npm run dev
```

**验证：** 打开 http://127.0.0.1:5173

### 默认管理员

```
工号：admin
密码：123456

⚠️⚠️ 上线务必改密码（改 .env 里的 DEFAULT_ADMIN_PASSWORD，或登录后在用户管理里重置）
```

---

## 三、数据库迁移（Alembic）

```bash
cd backend
source .venv/bin/activate

# 修改了 models 后，生成迁移脚本
alembic revision --autogenerate -m "add xxx table"

# 应用迁移（不丢旧数据）
alembic upgrade head

# 回滚一步
alembic downgrade -1

# 看当前版本
alembic current
```

**★ 为什么用 Alembic：**后续新增表/字段时，能平滑升级，不用删库重建。

---

## 四、如何新增一个模块（★ 最重要）

**以「器材管理」为例，三步：**

### ① 新建 model（`app/models/equipment.py`）

```python
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    count = Column(Integer, default=0)
```

**然后在 `app/models/__init__.py` 里 import 一下**（不 import，Alembic 检测不到）。

### ② 新建 schema（`app/schemas/equipment.py`）+ 新建 api（`app/api/equipment.py`）

**照抄 `api/users.py` 的写法**，把 `router = APIRouter(prefix="/equipment", tags=["器材"])`。

### ③ 在 `app/api/__init__.py` 里加一行

```python
from app.api import auth, users, tasks, equipment   # ← 加 equipment

routers = [
    auth.router,
    users.router,
    tasks.router,
    equipment.router,      # ← 加这一行
]
```

**④ 生成迁移 + 升级**

```bash
alembic revision --autogenerate -m "add equipment"
alembic upgrade head
```

**→ 完事。不用改 main.py，不用改前端路由（前端加个菜单项即可）。**

---

## 五、API 一览

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| POST | `/api/auth/login` | 公开 | 登录（返回 JWT）|
| GET | `/api/auth/me` | 登录 | 当前用户信息 |
| GET | `/api/users` | 管理员 | 用户列表 |
| POST | `/api/users` | 管理员 | 新增用户 |
| PUT | `/api/users/{id}` | 管理员 | 修改用户 |
| POST | `/api/users/{id}/reset-password` | 管理员 | 重置密码 |
| DELETE | `/api/users/{id}` | 管理员 | 删除用户 |
| GET | `/api/tasks/mine` | 登录 | 我的任务 |
| GET | `/api/tasks/{id}` | 本人/管理员 | 任务详情 |
| POST | `/api/tasks/{id}/submit` | 本人 | 提交任务 |
| GET | `/api/tasks/{id}/submissions` | 本人/管理员 | 提交记录 |
| POST | `/api/tasks/submissions/{id}/files` | 本人 | 上传附件 |
| GET | `/api/tasks/files/{id}/download` | 登录 | 下载附件 |
| GET | `/api/tasks` | 管理员 | 全部任务 |
| POST | `/api/tasks` | 管理员 | 发布任务 |
| PUT | `/api/tasks/{id}/status` | 管理员 | 审核/改状态 |
| DELETE | `/api/tasks/{id}` | 管理员 | 删除任务 |
| GET | `/api/tasks/admin/submissions` | 管理员 | 全部提交 |

**统一返回格式：**
```json
{ "code": 0, "msg": "ok", "data": { ... } }
```
`code = 0` 成功；非 0 为业务错误。

---

## 六、任务状态流转

```
pending（未开始）
   ↓ 管理员可手动改
doing（进行中）
   ↓ 队员提交
submitted（已提交，待审核）
   ├─ 管理员通过 → done（已完成）
   └─ 管理员驳回 → rejected（已驳回，填理由）
                      ↓ 队员重新提交 → submitted
```

---

## 七、安全要点

| 项 | 实现 |
|---|---|
| 密码存储 | bcrypt 哈希（不可逆）|
| 登录状态 | JWT（默认 12 小时过期）|
| 登录限流 | 同工号 5 分钟内最多 5 次失败 |
| 权限隔离 | 队员只能看/改自己的任务；管理员全权限 |
| 文件上传 | uuid 重命名（防路径穿越 + 防重名）+ 50MB 限制 |
| 附件下载 | 需登录 token |

**⚠️ 上线前必做：**
```
① .env 里换 SECRET_KEY（长随机串）
② 改默认管理员密码
③ 如果暴露到公网，加 HTTPS（本项目按内网设计，没做）
```

---

## 八、常见问题

| 现象 | 原因 | 解法 |
|---|---|---|
| `ValueError: password cannot be longer than 72 bytes` | bcrypt 4.1+ 与 passlib 1.7.4 不兼容 | `pip install "bcrypt==4.0.1"` |
| 前端 404 / CORS 报错 | 后端没启动，或端口不对 | 确认后端在 8000，看 `vite.config.js` 的 proxy |
| 登录后马上掉线 | token 过期或 SECRET_KEY 变了 | 重新登录 |
| 附件下载 404 | `static/uploads/` 里文件被删了 | 重新上传 |
| `alembic` 报 "Can't locate revision" | 数据库版本和迁移脚本不一致 | `alembic stamp head` 或删库重建 |

---

## 九、技术栈版本

```
Python 3.10+
FastAPI 0.115
SQLAlchemy 2.0
Alembic 1.13
Pydantic 2.9
bcrypt 4.0.1（★ 必须锁版本）

Node 18+
Vue 3.5
Element Plus 2.8
Vite 5.4
Pinia 2.2
```

---

## 十、后续可扩展的模块（已预留）

```
□ 器材管理（借还、库存）
□ 耗材申领（申请、审批）
□ 打卡（到实验室签到）
□ 文档库（规则手册、教程、笔记）
□ 标定记录（相机内参历史）
□ 比赛记录（对阵、复盘）
□ 代码仓库索引
```

**每个模块都是"三步 + 一行注册"，不用动原有代码。**
