# RTD 汉化文本项目

本项目管理已提取的原文、人工中文翻译及客户端使用的映射文件。当前所有中文单元格为空，**尚未完成汉化**；不提供机器翻译、不修改客户端业务数据，也不包含字体或 APK。Python 3.10+ 标准库即可运行，没有第三方依赖。

## 开始使用

1. 在支持 UTF-8 CSV 的编辑器中打开 `translations.csv`，只填写第二列“中文文本”。保留第一列“源文本”的每一个字符。
2. 在项目目录执行 `python scripts/export.py`。成功后生成 `dist/translation.json`，初始输出为 `{}`。
3. 执行 `python -m unittest discover -s tests -v` 运行校验测试。
4. 将 JSON 交给客户端项目；实际文件放置及 APK 打包遵循客户端说明。这里只生成交付文件，不部署或安装客户端。

从其他工作目录也可以执行 `python C:\你的目录\RTD_TRANSLATION\scripts\export.py`。复制整个项目到其他目录无需改代码。默认配置来自脚本所在项目根目录；所有可变路径集中于根 `rtd.config.json`，相对路径始终按项目根解析，与命令当前目录及配置文件位置无关。可通过 `--config C:\配置\rtd.config.json` 选取其他配置，绝对路径亦受支持。Windows 含空格路径请用引号。

## 目录

| 路径 | 用途 |
| --- | --- |
| `translations.csv` | 唯一主编辑表，恰好源文本、中文文本两列，UTF-8 BOM 便于 Excel 识别 |
| `sources/TextDatabase.txt` | 原始 UTF-8 制表符数据库，字节完整保留 |
| `sources/TextDatabase.json` | 全部 819 条 key/text 记录；key 只用于定位 |
| `sources/scene-labels.json` | 1,221 个 UILabel 的场景、对象 ID 与 mText 快照 |
| `sources/scene-distinct.csv` | 场景 425 条去重非空原文的单独参考表，不作为导出输入 |
| `sources/master-display-fields.json` | 主表中明确选择的显示字段原文，附表名、记录与业务 ID |
| `metadata/locations.json` | 原文 → 一个或多个来源位置，不在主 CSV 增列 |
| `metadata/coverage.json` | 数量、采集规则及原始输入 SHA-256 |
| `scripts/export.py` | 完整校验后原子写入 JSON |
| `docs/FORMAT.md` | 编辑规则和客户端共享契约 |
| `docs/DEVELOPMENT.md` | 数据维护、交付与验证边界 |
| `dist/` | 生成的交付文件，Git 忽略 |

采集快照为 2026-10-28：819 条 TextDatabase（751 条不同值）、1,211 次非空场景 mText（425 条不同值）、从 23 张已恢复主表读取的 12,902 次非空显示字段，共 14,932 个来源位置、9,693 条不同原文。业务 ID、资源名、URL、模型名及协议值未作为主表待译字段。场景包含遗留韩文与测试文本，不证明当前流程一定使用它们。未提取全部 DLL 常量、prefab、原生 Android、HTML 和图片文字。

本项目可独立编辑、校验和导出，不需要旧分析工程、游戏资源、服务端、Android SDK 或模拟器。运行中的游戏是否显示中文还取决于客户端显示钩子、模板覆盖以及旧 NGUI 中文位图字体，不能以导出成功替代设备验收。
