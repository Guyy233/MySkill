# 论文分析

将一篇英文或中文学术论文加工成两份中文 PDF：详细带读手册，以及中英对照三色批注译文。

## 适用场景

- 对论文进行带读、精读或逐段讲解
- 制作带前置知识、术语解释和自测题的阅读手册
- 生成中英对照译文，并以绿、黄、红三色标注结论、方法和局限
- 用原生 LaTeX 排版公式、变量和希腊字母，减少乱码与错位

## 运行要求

- 输入为论文 PDF 或完整论文文本
- 生成 PDF 时需要 XeLaTeX、CTeX 和 XeCJK
- 模板默认使用 macOS 的 `PingFang SC`；其他系统可改为 `Noto Sans CJK SC` 等字体

## 主要文件

- `SKILL.md`：完整工作流、写作标准、三色规则和校验要求
- `assets/preamble.tex`：字体、公式、三色高亮与版式定义
- `assets/guide_template.tex`：带读手册骨架
- `assets/translation_template.tex`：中英对照三色批注译文骨架
