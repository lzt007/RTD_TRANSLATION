# 维护与交付说明

## 开发环境与路径

安装 Python 3.10 或更新版本后即可执行，不需要 pip 安装。根 `rtd.config.json` 的 `paths.csv` 与 `paths.output` 是导出器读取和写入的位置；`sources`、`locations`、`coverage` 是资料索引路径。所有相对值按项目根解释。配置文件本身默认在根目录，命令行 `--config` 的相对参数按当前目录解释；这不改变配置内路径的解释方式。

项目不启动网络服务、不读取真实存档，也不需要任何其他工程目录。源码和文本原文可纳入版本控制，生成 `dist/`、Python 缓存和虚拟环境忽略。未保存签名密钥、数据库、完整资源包或第三方工具。

## 原文来源和维护

`TextDatabase.txt` 来自原 sharedassets1.assets 的 TextDatabase 对象 28；UTF-8 字节 SHA-256 是 `7fce2f36935e473338862cb99d7a745db2ef0d271810641b545db3fe0ba16bf0`。第一个 tab 分段为 819，后续严格交替 key/value 共 1,638 段；值包含真实换行。JSON 仅方便查阅，原始字节文件是对照依据。

场景来自既有 `scene-fields.json` 中 script 为 UILabel 的字段，仅保留场景名、path_id、offset 和原始 mText，空值也保存在来源快照中；主翻译表只收非空值。该索引不代表所有 prefab 或所有运行时标签。

主表从既有 `*_MASTER.json` 的 result/data_list 选择 `name`、`text`、`story`、`ct_text`、`sct_text`、`sct6_text`、`a_skill_text`、`target_name`、`info_message_0/1`、`lock_message`、`unlock_message` 及 `message_<数字>`。不抓取所有字符串字段，避免把 id、日期、模型/纹理/图标/横幅资源名当作译文。空字符串跳过，其余字符原样保留。来源保留原业务 ID，不能翻译或回写到服务器主数据。`coverage.json` 记录 23 个原输入文件校验值；项目只带抽取后的显示字段，不带响应 session。

`locations.json` 以原文为键，包含一个或多个来源对象：`file` 是项目内来源快照，`record` 为从 0 开始的数组下标；TextDatabase 附 `key`，场景附 `scene/path_id/field`，主表附 `table/result_index/record_index/business_id/field`。同源文多个位置共享一个译文；语境冲突应记录待办并交由客户端设计上下文覆盖，不能破坏两列契约。

本次采集是离线快照，没有默认连接旧分析工程的“自动刷新”。后续追加新来源时应提供提取证据、校验值与范围，先更新来源快照和索引，再按精确原文合并主 CSV，保留已有中文。不要对原文做 Unicode/换行规范化；原文删除也应人工审查。新增 DLL 字符串必须确认是显示文本，新增图片文字需要独立图像流程。

## 校验与交付流程

```powershell
python scripts/export.py
python -m unittest discover -s tests -v
Get-FileHash dist/translation.json -Algorithm SHA256
```

先处理全部导出错误，再将本轮 JSON 及其 SHA-256 交付客户端维护者。建议交付记录注明 CSV 版本、非空译文数量、目标客户端版本和需要验证的界面。不要将包含测试译文的临时表覆盖正式原表。

测试覆盖真实 819 条数据库与主表原文集合、425 条场景去重值、两列与初始空译文、跨工作目录执行、CSV BOM/逗号/引号/CRLF、重复冲突、占位符格式和 NGUI 标记保护。它证明导出与静态数据一致，不证明实际字体、布局、性能或动态文本全部覆盖。

客户端需在独立候选 APK 上验证：空字典时正常显示原文、固定标签命中、格式化模板、长剧情换行、中文/日文/数字字形共存以及资源失败回退。旧 NGUI 使用位图字体，简单加入 TTF 或一份 JSON 不能保证中文显示；本项目未制作字体也未进行模拟器验收。
