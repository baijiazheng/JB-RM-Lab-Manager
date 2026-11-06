# encoding: utf-8
"""★★★ 路由注册中心（唯一的扩展点）

新增模块（器材管理 / 耗材申领 / 打卡 / 文档库 / 标定记录 ...）时：
  ① 在 api/ 下新建 xxx.py，里面 router = APIRouter(prefix="/xxx", tags=["xxx"])
  ② 在下面 import 并 routers.append(xxx.router)
  ③ 完事 —— 不用改 main.py，不用改其他任何文件

类比：这就是 Django 的 urls.py、Spring 的 @ComponentScan
"""
from app.api import auth, users, tasks

routers = [
    auth.router,
    users.router,
    tasks.router,
    # ▼▼▼ 新模块往这里加 ▼▼▼
    # equipment.router,      # 器材管理
    # consumable.router,     # 耗材申领
    # attendance.router,     # 打卡
    # docs.router,           # 文档库
    # calibration.router,    # 标定记录
]
