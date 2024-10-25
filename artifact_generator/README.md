# Wheel Artifact Generator

This folder includes all the code necessary to generate dummy wheels supporting different variants.
As of today `python -m build` does not support `variant` declaration. So "fake it until you make it".

## Process:

### Developer

```bash
make build  # Generate the base wheel
make generate_variants  # Generate N copies (of above wheel) with variant information
```

### Push to Prod

In order to push to prod into the `/artifacts` folder:

`make build_all`

This will do all the above and copy the result into the right folder.