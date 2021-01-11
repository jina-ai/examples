# Submit Your Community Example!

Thanks for your interest in submitting your example! Here are some rules and guidelines:

## Rules

### `jina` in `requirements.txt`

To be eligible for listing, you **must** have `jina==x.x.x` in your `requirements.txt`, where `x.x.x` refers to the semantic version number.

Note: If you're building a front-end that just interfaces with Jina's API and doesn't rely on Jina core itself, there's no need to follow this requirement.

### `jina-` at start of name

Your repo name should be `jina-xxxxxxx`.

### Clear README

- Explain what your example does and how to run it

### Use scripts to get external resources

- **For datasets:** Use a script named `get_data.sh`
- **For models**: If you use an externally-hosted model, call your script `get_model.sh` or similar
- **For other assets:** Follow the `get_xxx.sh` pattern

### `.gitignore` and `.dockerignore`

Have a `.gitignore` file and list any directories that should be ignored. The same goes for `.dockerignore` if you have `Dockerfile`:

- `data` directory
- `workspace` directory
- virtual environment directories
- directories that store assets retrieved by [scripts](#use-scripts-to-get-external-resources)

### License

You **must** use an open-source license, specified in `LICENSE` in the root of your repo

## Guidelines

We're more easy-going on these

### One Example Per Repo

To make code more maintainable and easier for end users, please include one example per repo.

### Tests

Please include tests to ensure your app or Pod works correctly.

### File Structure

- Please follow the file structure as created by `jina hub new --type app`
- Store data in `data` and externally-downloaded models in `models`

### Dockerfile

We highly encourage you to add a `Dockerfile`.

### Docker image

For self-contained apps, we would love to host a Docker image on [Jina Hub](https://github.com/jina-ai/jina-hub)
