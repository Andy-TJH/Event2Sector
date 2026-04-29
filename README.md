# Event2Sector

**隔夜新闻 / 政策 / 商品价格 / 海外市场事件 → A股板块映射 → 相关个股 → 盘前报告**

## 项目简介

Event2Sector 是一个自动化盘前分析工具，核心流程：

1. **新闻输入** — 从 JSON 文件加载隔夜新闻（后续可接入实时新闻源）
2. **事件识别** — 基于关键词 + 条件正则匹配，从新闻中抽取结构化事件
3. **板块映射** — 根据预定义规则，将事件映射为 A 股板块影响（利好/利空）
4. **个股匹配** — 通过公司标签库，找到受影响板块下的相关个股
5. **报告生成** — 输出结构化 Markdown 盘前日报

## 快速开始

```bash
# 克隆项目
git clone <repo-url>
cd Event2Sector

# 安装（纯 Python，无第三方依赖）
pip install -e .

# 使用示例新闻生成报告
event2sector examples/sample_news.json

# 或直接运行
python -m event2sector.cli examples/sample_news.json
```

## 项目结构

```
Event2Sector/
├── README.md
├── pyproject.toml
├── .env.example
├── configs/
│   ├── sector_rules.json        # 事件 → 板块影响规则
│   └── stock_tags.json          # A股公司标签库
├── event2sector/
│   ├── cli.py                   # 命令行入口
│   ├── models.py                # 数据模型
│   ├── data_sources/            # 新闻源适配器
│   ├── event_extractor/         # 事件抽取模块
│   ├── impact_mapper/           # 板块/个股映射模块
│   ├── market_validator/        # T+1/T+3/T+5 验证（预留）
│   ├── report_generator/        # Markdown 报告生成
│   └── storage/                 # SQLite 存储（预留）
├── examples/
│   └── sample_news.json         # 示例新闻
├── reports/                     # 生成的报告
├── tests/
└── docs/
```

## 配置说明

### sector_rules.json

定义事件到板块的映射规则，每条规则包含：
- `keywords` — 触发关键词列表
- `condition` — 方向性条件正则（如"上涨|飙升"）
- `sectors` — 影响的板块列表及方向

### stock_tags.json

A 股公司标签库，每只股票标注所属板块，用于个股匹配。

## 命令行参数

```
event2sector <news_json> [--rules PATH] [--stocks PATH] [--output DIR] [--date YYYY-MM-DD]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `news_json` | 新闻 JSON 文件路径 | 必填 |
| `--rules` | 板块规则文件 | `configs/sector_rules.json` |
| `--stocks` | 个股标签库 | `configs/stock_tags.json` |
| `--output` | 报告输出目录 | `reports/` |
| `--date` | 报告日期 | 当天日期 |

## 后续规划

- [ ] 接入实时新闻源（RSS / API）
- [ ] LLM 辅助事件抽取（替代纯规则）
- [ ] T+1 / T+3 / T+5 市场验证模块
- [ ] SQLite 历史存储与回测
- [ ] Web UI 展示
