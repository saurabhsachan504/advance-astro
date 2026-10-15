# Vision service boundary

This directory is deliberately a contract, not an unvalidated fortune-telling model. Before enabling it, implement the pipeline below as an isolated service:

1. Malware/MIME/magic-byte validation and image decompression limits.
2. EXIF stripping and encrypted temporary storage.
3. Palm segmentation or face-image quality checks using a commercially permitted model.
4. Non-identifying feature JSON with confidence levels.
5. Raw image deletion and key destruction according to the chosen retention policy.

Never implement identity matching, face embeddings, demographics, emotion recognition, health inferences, or surveillance. Route only approved feature JSON to the report service—never the raw photo.

