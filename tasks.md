# Tasks - Multi-Agent Research Lab

## Mục tiêu
- Hoàn thiện hệ thống nghiên cứu multi-agent gồm: `Supervisor`, `Researcher`, `Analyst`, `Writer` (và `Critic` nếu kịp).
- Chạy được baseline single-agent và so sánh với multi-agent bằng báo cáo benchmark.
- Có trace/log đủ để giải thích luồng hoạt động và failure mode.

## Ưu tiên P0 (bắt buộc để chạy end-to-end)
- [x] Setup môi trường và config
  - [x] Tạo env, cài dependency, copy `.env.example` thành `.env`.
  - [x] Điền `OPENAI_API_KEY` và chọn model trong `.env`.
  - [x] Chạy `make test` để xác nhận skeleton pass.
- [x] Implement LLM client
  - [x] Hoàn thiện `LLMClient.complete` tại `src/multi_agent_research_lab/services/llm_client.py`.
  - [x] Thêm retry/timeout tối thiểu, mapping lỗi rõ ràng.
- [x] Implement search client
  - [x] Hoàn thiện `SearchClient.search` tại `src/multi_agent_research_lab/services/search_client.py`.
  - [x] Chuẩn hóa output nguồn: title/url/snippet/source.
- [x] Implement các worker agents
  - [x] `ResearcherAgent.run` tại `src/multi_agent_research_lab/agents/researcher.py`.
  - [x] `AnalystAgent.run` tại `src/multi_agent_research_lab/agents/analyst.py`.
  - [x] `WriterAgent.run` tại `src/multi_agent_research_lab/agents/writer.py`.
- [x] Implement supervisor/router
  - [x] `SupervisorAgent.run` tại `src/multi_agent_research_lab/agents/supervisor.py`.
  - [x] Định nghĩa policy handoff + điều kiện dừng (`max_iterations`, `timeout_seconds`).
- [x] Định nghĩa/mở rộng shared state schema
  - [x] Cập nhật `ResearchState` tại `src/multi_agent_research_lab/core/state.py` đủ field cho handoff giữa các agent.
  - [x] Thêm input validation (Pydantic) cho query đầu vào và output từng agent.
- [x] Build workflow graph
  - [x] `MultiAgentWorkflow.build` tại `src/multi_agent_research_lab/graph/workflow.py`.
  - [x] `MultiAgentWorkflow.run` tại `src/multi_agent_research_lab/graph/workflow.py`.
  - [x] Đảm bảo state cập nhật nhất quán giữa các node.
- [x] Cập nhật baseline thật
  - [x] Thay baseline placeholder trong `src/multi_agent_research_lab/cli.py` bằng single-agent call thật.

## Ưu tiên P1 (chất lượng + quan sát)
- [ ] Observability/tracing
  - [ ] Hoàn thiện hook trace tại `src/multi_agent_research_lab/observability/tracing.py`.
  - [ ] Gắn `run_id`, agent name, latency, status theo từng step.
- [ ] Đánh giá benchmark
  - [ ] Hoàn thiện metric trong `src/multi_agent_research_lab/evaluation/benchmark.py`.
  - [ ] Bổ sung báo cáo trong `src/multi_agent_research_lab/evaluation/report.py`.
  - [ ] So sánh `single-agent` vs `multi-agent`: quality, latency, cost, lỗi.
- [ ] Optional quality gate
  - [ ] Implement `CriticAgent.run` tại `src/multi_agent_research_lab/agents/critic.py`.
  - [ ] Tích hợp critic vào graph như bước hậu kiểm.

## Ưu tiên P2 (tài liệu nộp bài)
- [ ] Hoàn thiện `docs/design_template.md`.
- [ ] Hoàn thiện các mục TODO trong `docs/lab_guide.md`.
- [ ] Tạo `reports/benchmark_report.md` có:
  - [ ] Bảng kết quả benchmark.
  - [ ] Ví dụ output tốt/xấu.
  - [ ] Phân tích failure mode + cách fix.
  - [ ] Link/screenshot trace.

## Checklist nộp bài
- [ ] GitHub repo cá nhân đã push code hoàn chỉnh.
- [ ] Screenshot trace hoặc link trace (LangSmith / Langfuse / OpenTelemetry).
- [ ] `reports/benchmark_report.md` so sánh single vs multi-agent.
- [ ] Đoạn giải thích failure mode và cách fix (trong report hoặc README).

## Smoke test cuối cùng
- [ ] Chạy baseline:
  - [ ] `python -m multi_agent_research_lab.cli baseline --query "..."`
- [ ] Chạy multi-agent:
  - [ ] `python -m multi_agent_research_lab.cli multi-agent --query "..."`
- [ ] Chạy test:
  - [ ] `make test`
- [ ] Xác nhận không còn `TODO(student)` trong các phần bắt buộc P0.

## Definition of Done
- [ ] Không còn raise `StudentTodoError` ở flow P0.
- [ ] Multi-agent run hoàn chỉnh và trả về câu trả lời có nguồn tham chiếu.
- [ ] Có benchmark report single vs multi-agent.
- [ ] Có trace/log đủ để trình bày trong phần review.
