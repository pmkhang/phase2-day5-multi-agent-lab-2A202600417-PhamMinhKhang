# Design Template

## Problem

Hệ thống cần xử lý các truy vấn nghiên cứu phức tạp (ví dụ: "GraphRAG state-of-the-art") và
tổng hợp thành báo cáo có cấu trúc, có trích dẫn nguồn. Single-agent không đủ vì phải đồng thời
tìm kiếm, phân tích, và viết — dễ bỏ sót nguồn hoặc thiếu phân tích sâu.

## Why multi-agent?

Single-agent xử lý tuần tự toàn bộ pipeline trong một prompt, dẫn đến:
- Không tách biệt được retrieval và reasoning → dễ hallucinate
- Không có bước kiểm tra chất lượng độc lập
- Khó debug khi output sai (không biết bước nào lỗi)

Multi-agent cho phép mỗi agent chuyên sâu một nhiệm vụ, có shared state rõ ràng để trace,
và Supervisor kiểm soát luồng để tránh vòng lặp vô hạn.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Quyết định agent nào chạy tiếp theo, dừng khi đủ điều kiện | `ResearchState` (iteration, notes, answer) | `route_history` cập nhật | Loop vô hạn nếu thiếu `max_iterations` |
| Researcher | Tìm kiếm nguồn và tạo research notes | `request.query`, `max_sources` | `sources`, `research_notes` | Trả về fallback nếu Tavily lỗi hoặc không có key |
| Analyst | Phân tích notes thành insights có cấu trúc | `research_notes`, `sources` | `analysis_notes` | Output heuristic nếu không dùng LLM |
| Writer | Tổng hợp final answer từ notes + analysis | `research_notes`, `analysis_notes`, `sources` | `final_answer` | LLM timeout hoặc empty response |

## Shared state

`ResearchState` (Pydantic model) — fields và lý do:

| Field | Lý do |
|---|---|
| `request` | Query gốc + config (max_sources, audience) |
| `run_id` | Trace ID duy nhất cho mỗi lần chạy |
| `iteration` | Guardrail chống loop vô hạn |
| `route_history` | Audit trail để debug luồng chạy |
| `sources` | Danh sách SourceDocument để Writer trích dẫn |
| `research_notes` | Tóm tắt từ Researcher, input cho Analyst |
| `analysis_notes` | Insights từ Analyst, input cho Writer |
| `final_answer` | Output cuối cùng trả về user |
| `agent_results` | Log kết quả từng agent (token count, metadata) |
| `trace` | Danh sách trace events cho observability |
| `errors` | Lỗi runtime để tính error_rate trong benchmark |

## Routing policy

```
START
  └─> Supervisor
        ├─ sources/research_notes trống  ──> Researcher
        ├─ analysis_notes trống          ──> Analyst
        ├─ final_answer trống            ──> Writer
        ├─ enable_critic & no critic     ──> Critic (optional)
        ├─ iteration >= max_iterations   ──> done
        └─ tất cả đã có                  ──> done
```

## Guardrails

- Max iterations: `MAX_ITERATIONS=6` (env), mặc định 6 — Supervisor kiểm tra mỗi bước
- Timeout: `TIMEOUT_SECONDS=60` — cấu hình sẵn, áp dụng ở tầng HTTP client
- Retry: SearchClient tự fallback sang offline sources nếu Tavily lỗi
- Fallback: LLMClient trả `[offline-fallback]` nếu không có API key nào
- Validation: Pydantic schema validate input/output; `ResearchQuery.query` min_length=5

## Benchmark plan

Query: `"Research GraphRAG state-of-the-art and write a 500-word summary"`

Metrics:
- `latency_seconds` — thời gian end-to-end
- `quality_score` — heuristic 0–10 dựa trên completeness của state
- `citation_coverage` — % source titles xuất hiện trong final answer
- `error_rate` — số lỗi / số bước
- `estimated_cost_usd` — ước tính từ token count

Expected outcome:
- Multi-agent có quality cao hơn (có research + analysis notes → +3.5 điểm so với baseline)
- Single-agent nhanh hơn (1 LLM call vs nhiều bước)
- Multi-agent có citation coverage rõ ràng, single-agent không có (không có sources)
