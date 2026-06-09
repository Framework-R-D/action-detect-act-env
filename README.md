# `action-detect-act-env`

> Detects if the workflow is running under `act` (local GitHub Actions testing tool).

## Usage

```yaml
- uses: Framework-R-D/action-detect-act-env@v1  # pin to commit SHA in production
  with:
    input-name: value
```

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
(none)

## Outputs

| Name | Description |
|------|-------------|
| `is_act` | True if running in act, false otherwise |

## License

[Apache 2.0](LICENSE)
