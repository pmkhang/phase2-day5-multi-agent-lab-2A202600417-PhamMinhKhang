# Lab Guide: Multi-Agent Research System

## Scenario

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Single-agent baseline**: một agent làm toàn bộ.
2. **Multi-agent workflow**: Supervisor điều phối Researcher, Analyst, Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có responsibility riêng.
- Shared state phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ nhìn output bằng cảm tính.

## Milestone 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

**Đã implement**: `LLMClient.complete` gọi OpenAI-compatible API qua 9Router (`NINEROUTER_URL`).
Nếu không có API key, trả về `[offline-fallback]` để workflow vẫn chạy được.
Retry/timeout được xử lý ở tầng HTTP client của OpenAI SDK.

## Milestone 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

**Routing policy đã implement**:

- Nếu chưa có `sources` / `research_notes` → gọi **Researcher**
- Nếu chưa có `analysis_notes` → gọi **Analyst**
- Nếu chưa có `final_answer` → gọi **Writer**
- Nếu `enable_critic=true` và chưa có `critic_notes` → gọi **Critic**
- Nếu `iteration >= max_iterations` hoặc tất cả đã có → **done**

Nếu agent fail (có `state.errors`), workflow dừng sớm thay vì retry vô hạn.

## Milestone 3: Worker agents

File gợi ý:

- `agents/researcher.py`
- `agents/analyst.py`
- `agents/writer.py`

**Đã implement**:

- **Researcher**: gọi `SearchClient.search` (Tavily nếu có key, offline fallback nếu không).
  Output: `state.sources` (list `SourceDocument`) + `state.research_notes` (bullet list).
- **Analyst**: tổng hợp `research_notes` thành `analysis_notes` có cấu trúc (key findings, risks).
- **Writer**: gọi LLM với `research_notes` + `analysis_notes` → `final_answer` có section `Sources:`.
- **Critic** (optional, `ENABLE_CRITIC=true`): kiểm tra citation coverage và độ dài answer.

## Milestone 4: Trace và benchmark

File gợi ý:

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

**Đã implement**:

- `trace_span` context manager gắn `run_id`, agent name, latency, status vào mỗi bước.
- Langfuse v4 integration: mỗi run tạo 1 trace với 3 spans (researcher/analyst/writer).
  Xem trace tại: https://cloud.langfuse.com (project `multi-agent-research-lab`).
- Benchmark đo: latency, quality score (heuristic 0–10), citation coverage, error rate, token count, cost.

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | wall-clock time |
| Cost | token usage × price/token |
| Quality | heuristic: +2 final_answer, +1.5 research_notes, +1.5 analysis_notes |
| Citation coverage | số source titles xuất hiện trong final_answer / tổng sources |
| Failure rate | số lỗi / số bước trong route_history |

## Exit ticket

1. **Case nào nên dùng multi-agent?**
   Khi task có thể tách thành các bước độc lập với input/output rõ ràng (retrieve → analyze → write),
   cần traceability từng bước, hoặc cần chạy song song nhiều subtask. Multi-agent giúp debug dễ hơn
   vì biết chính xác bước nào fail.

2. **Case nào không nên dùng multi-agent?**
   Khi task đơn giản, latency quan trọng hơn quality, hoặc context cần được giữ liên tục xuyên suốt
   (multi-agent handoff qua state có thể mất context tinh tế). Overhead orchestration không đáng
   nếu single LLM call đã đủ tốt.
