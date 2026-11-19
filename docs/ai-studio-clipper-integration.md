# Google AI Studio Clipper — Integration Brief

User-provided app:
https://ai.studio/apps/1db01e2d-5df3-47d0-9ffc-04712ff4253a

## Access status
The link has been supplied by the owner, but this environment could not load the app. Google AI Studio apps may require the owner's signed-in Google session. No source code, configuration, or runtime behavior has been inspected or verified.

## Intended role in AURA
Treat the existing clipper as a potential production tool, not as a verified working integration. AURA should orchestrate:
1. Discover a source video that is owned, licensed, permissioned, or otherwise lawfully usable.
2. Record source URL/file, owner, license/permission evidence, and allowed platforms.
3. Send approved media and a clipping brief to the clipper.
4. Receive candidate clips, transcripts, timestamps, captions, and metadata where supported.
5. Run quality, factual, rights, and platform-policy checks.
6. Require human approval before public publishing.
7. Track published URL and performance.

## Required inspection before integration
- App source code or exported project files.
- Framework/runtime and dependency list.
- Input and output schema.
- Whether it uses Gemini API or other paid services; estimate usage/cost.
- Whether it accepts local uploads, YouTube URLs, or other media sources.
- Whether it downloads, stores, or transmits media; storage/retention behavior.
- How clips are selected, rendered, captioned, and exported.
- Authentication, API keys, and secrets handling.
- Current known limitations and deployment target.

## Integration options
A. API/service integration if the app exposes a stable authenticated endpoint.
B. Shared backend/library if the app source can be exported and safely incorporated.
C. Manual handoff with structured AURA briefs and output uploads if no API is available.

Do not scrape or automate the private AI Studio UI as a substitute for an API. Do not put Gemini keys or other secrets in client-side code or GitHub.

## Owner handoff needed
Provide one of:
- exported source/project files, or
- a public, non-secret source repository, or
- screenshots of the app's input screen, output screen, and settings plus its generated code.

Never send API keys, passwords, OTPs, or recovery codes in chat.
