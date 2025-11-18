# API - 搜索接口

> **文档版本**: v2.0  
> **最后更新**: 2025-01-17

这些接口为 Agent 提供了执行 Web 搜索的能力，以获取外部信息和知识。

**Base Path**: `/search`

## 先决条件

要使用这些接口，您必须在 `backend/.env.dev` 文件中配置至少一个搜索引擎的 API Key。

-   `TAVILY_API_KEY`: [Tavily AI](https://tavily.com/) 的 API Key。
-   `EXA_API_KEY`: [Exa AI](https://exa.ai/) 的 API Key。

## 接口列表

-   `POST /search/web`: 执行 Web 搜索。
-   `POST /search/content`: 获取多个 URL 的内容（仅 Exa）。
-   `POST /search/similar`: 查找与 URL 相似的页面（仅 Exa）。

---

### `POST /search/web`

**描述**: 使用配置的默认搜索引擎（或请求中指定的引擎）执行 Web 搜索。

**请求体 (JSON)**:

```json
{
  "query": "applications of linear programming in supply chain",
  "provider": "tavily",
  "num_results": 5,
  "search_depth": "advanced",
  "include_domains": ["wikipedia.org"],
  "exclude_domains": ["ads.com"]
}
```
-   `query` (string, required): 搜索查询字符串。
-   `provider` (string, optional): 指定要使用的搜索引擎。允许的值: `"tavily"`, `"exa"`。如果未提供，则使用 `SEARCH_DEFAULT_PROVIDER` 环境变量配置的默认值。
-   `num_results` (integer, optional): 希望返回的结果数量。默认为 10。
-   `search_depth` (string, optional): [Tavily only] 搜索深度。允许的值: `"basic"`, `"advanced"`。`advanced` 会进行更深入的搜索和内容总结，但速度较慢。
-   `include_domains` (array of strings, optional): [Tavily only] 仅在这些域名中搜索。
-   `exclude_domains` (array of strings, optional): [Tavily only] 从搜索结果中排除这些域名。

**成功响应 (`200 OK`)**:

```json
{
  "query": "applications of linear programming in supply chain",
  "results": [
    {
      "title": "Linear Programming: Applications, Advantages, and Disadvantages",
      "url": "https://www.investopedia.com/terms/l/linear-programming.asp",
      "content": "Linear programming is a method to achieve the best outcome in a mathematical model whose requirements are represented by linear relationships... In supply chain management, it is used for optimizing logistics.",
      "score": 0.98,
      "published_date": "2023-10-26"
    },
    {
      "title": "Supply Chain Optimization with Linear Programming",
      "url": "https://towardsdatascience.com/supply-chain-optimization-with-linear-programming-4a6f4e2f3fe8",
      "content": "A practical guide to using linear programming for supply chain challenges, including transportation, inventory, and production planning.",
      "score": 0.95,
      "published_date": null
    }
  ],
  "provider": "tavily",
  "total_results": 5
}
```

**错误响应**:
-   `400 Bad Request`: 如果配置的搜索引擎 API Key 无效或请求参数不正确。

---

### `POST /search/content`

**描述**: [仅 Exa] 获取一个或多个 URL 的完整、清洁的文本内容。这比直接抓取网页更可靠。

**请求体 (JSON)**:

```json
{
  "urls": [
    "https://www.investopedia.com/terms/l/linear-programming.asp",
    "https://towardsdatascience.com/supply-chain-optimization-with-linear-programming-4a6f4e2f3fe8"
  ]
}
```
-   `urls` (array of strings, required): 要获取内容的 URL 列表。

**成功响应 (`200 OK`)**:

```json
{
  "https://www.investopedia.com/terms/l/linear-programming.asp": "Linear programming (LP) is a method to achieve the best outcome...",
  "https://towardsdatascience.com/supply-chain-optimization-with-linear-programming-4a6f4e2f3fe8": "In today’s complex global market, optimizing the supply chain is not just an advantage; it’s a necessity..."
}
```

**错误响应**:
-   `400 Bad Request`: 如果 `urls` 列表为空，或者 Exa API Key 未配置。

---

### `POST /search/similar`

**描述**: [仅 Exa] 查找与给定 URL 内容相似的网页。

**请求体 (JSON)**:

```json
{
  "url": "https://www.investopedia.com/terms/l/linear-programming.asp",
  "num_results": 3
}
```
-   `url` (string, required): 用于查找相似页面的源 URL。
-   `num_results` (integer, optional): 希望返回的结果数量。默认为 10。

**成功响应 (`200 OK`)**:

返回一个与 `/search/web` 格式相同的搜索结果列表。

```json
[
  {
    "title": "What Is Linear Programming? Assumptions, Properties, and Methods",
    "url": "https://www.spiceworks.com/tech/data-management/articles/what-is-linear-programming/",
    "content": "Linear programming is a mathematical modeling technique used to optimize a linear objective function...",
    "score": 0.92,
    "published_date": "2023-05-15"
  }
]
```

**错误响应**:
-   `400 Bad Request`: 如果 `url` 为空，或者 Exa API Key 未配置。

## 📚 相关文档

-   [API 概览](overview.md)
-   [指南 - 模型配置](../guides/model-configuration.md)
-   [参考 - 环境变量](../reference/environment-variables.md)

---

**上一页**: [WebSocket 接口](websocket.md)  
**下一页**: [设置接口](settings.md)
