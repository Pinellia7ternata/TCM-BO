# w3id 永久标识符申请说明

## 背景

本体当前命名空间为 `http://OntoTCM.org.cn/ontologies/TCM_TO`。投稿材料里承诺提供 persistent (w3id) identifiers，有两种落地方式，**建议选方案 A**：

### 方案 A（推荐）：自有域名 + w3id 双轨

- 短期：先在 GitHub 公开仓库，w3id 申请一个组织命名空间（如 `https://w3id.org/tcm-bo/`），重定向到 GitHub 仓库与原始 OWL 文件；
- 长期：`OntoTCM.org.cn` 域名恢复可控后做同样的 content negotiation，w3id 作为永不失效的备份入口。

### 方案 B：整体迁移到 w3id 命名空间

把 ontology IRI 与所有实体 IRI 改为 `https://w3id.org/tcm-bo/TCM_TO#...`。改动面大（需全库重命名 + 重跑验证链），仅在未来主版本（如 2.0）考虑。

## 申请步骤（w3id.org 标准流程）

1. Fork `https://github.com/perma-id/w3id.org`；
2. 在仓库根目录新建 `tcm-bo/` 目录，放入本目录下的 `.htaccess`（把 `<GITHUB_ORG>` 替换为实际 GitHub 组织/用户名）；
3. 同目录放一个 `README.md`，写明维护者（Chao Chen / 陈超，chenchao_0727@163.com）与 GitHub ID（w3id 硬性要求，GitHub ID 建仓后补填）；
4. 提 PR 到 perma-id/w3id.org，标题如 `Add tcm-bo namespace`，正文简述用途（TCM body-structure ontology, CC-BY 4.0, journal submission in preparation）；
5. 合并后 `https://w3id.org/tcm-bo/ontology` 即可永久解析到本体文件。

## .htaccess 生效后的解析行为

| 请求 | 重定向到 |
|---|---|
| `https://w3id.org/tcm-bo/` | GitHub 仓库首页 |
| `https://w3id.org/tcm-bo/ontology` | 当前发布版 OWL 文件（raw） |
| `https://w3id.org/tcm-bo/ontology/1.9.17` | 1.9.17 版 OWL 文件（raw，按 release tag 固定） |

> BioPortal / Ontobee 上架时填写的 ontology URL 就用 `https://w3id.org/tcm-bo/ontology`。
