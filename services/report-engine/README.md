# Report engine contract

The report engine receives a `ChartSnapshot`, optional approved `VisionAnalysis`, user question and retrieved licensed source chunks. It must return schema-validated JSON with cited sources, confidence/caveat fields, and no invented calculation facts.

Run local model serving (vLLM/NIM) separately. Keep model weights, source books, prompts containing private data, and generated reports off public logs and external APIs.

