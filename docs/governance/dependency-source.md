# Python 依赖源配置建议（国内可选）

为保证仓库可移植性，项目默认不强制绑定国内镜像。

## 1. 一次性安装（推荐）

```bash
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

对于当前阶段（使用 `pyproject.toml`），可按需执行：

```bash
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi==0.115.0 uvicorn==0.30.6 pydantic==2.9.2 pytest==8.3.3 httpx==0.27.2
```

## 2. 永久配置（Windows）

在 `%APPDATA%\\pip\\pip.ini` 写入：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
```

## 3. 永久配置（Linux/macOS）

在 `~/.pip/pip.conf` 写入：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
```

## 4. 回退到官方源

删除上述本地配置文件，或临时使用：

```bash
python -m pip install -i https://pypi.org/simple <package>
```

## 5. 说明

- 该策略仅影响开发机安装速度，不改变仓库依赖定义。
- CI 环境可按部署地区选择是否启用镜像源。
