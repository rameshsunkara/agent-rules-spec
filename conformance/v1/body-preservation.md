---
spec-version: 1
name: body-preservation
description: Preserve the Markdown body exactly
activation: always
---

# Body preservation

  This line intentionally starts with two spaces.

```yaml
---
this-is-body: true
---
```

The final line has no special normalization requirement beyond UTF-8 preservation.
