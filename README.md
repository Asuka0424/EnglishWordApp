# 英语单词本 English Wordbook

一个使用 Python `tkinter` 编写的 Windows 桌面英语单词记忆工具。

## 功能

- 添加英文单词、中文释义和可选例句
- 按英文、释义或例句搜索
- 标记 0–5 级熟练程度
- 复习到期单词，并根据回答调整熟练程度和下次复习日期
- 将词库保存在本地 `words.json`

## 运行

安装 Python 3 后，在项目目录的终端运行：

```bash
python main.py
```

本项目只使用 Python 标准库，不需要安装额外的第三方包。

## 数据说明

程序第一次添加单词后会在项目目录创建 `words.json`。这个文件只保存在自己的电脑上，并且已加入 `.gitignore`，不会随代码上传到 GitHub。
