# 自动化文档处理微创业项目 (AutoDoc-Agent)

## 项目背景
本项目旨在通过 AI Agent 技术（以 Gemini API 为核心，Gemini CLI 为辅助）实现办公文档的自动化处理。重点解决学术论文排版、高保真 PDF 转 Word、以及基于模板的教案/报告生成等高价值需求。

## 核心架构
1.  **智能排版代理 (Styling Agent)**: 负责样式映射与样式表操控，使用 `python-docx`。
2.  **PDF 解析代理 (Parsing Agent)**: 负责多模态分离与 OCR，集成 `MinerU` / `PyMuPDF`。
3.  **模板渲染代理 (Rendering Agent)**: 负责“填空式”生成，使用 `docxtpl`。
4.  **视觉插图代理 (Visual Agent)**: 负责 Mermaid/TikZ 矢量图生成。

## 关键技术栈
- **环境**: Linux (代码、库、处理过程临时文件均存储在 Linux 环境中)
- **模型**: Gemini API (主要逻辑与分析判断)
- **库**: `python-docx`, `docxtpl`, `PyMuPDF`, `MinerU`
- **输出**: 最终生成的成果文件（如 JPG, SVG, DOC 等）输出并保存至指定的 Windows 系统挂载位置。

## 开发计划 (MVP)
- [ ] 环境搭建 (WSL2 + Python Venv)
- [ ] 教案模板渲染原型实现 (`docxtpl`)
- [ ] 集成 Gemini API 调度脚本
- [ ] 实现带水印的预览 PDF 生成
- [ ] 备份机制与 GitHub 同步

## 商业模式
- 按页收费 (2-10元/页)
- 防白嫖：先发带水印预览 PDF，确认后再发 Word 源文件。
- 推广渠道：小红书、闲鱼。
