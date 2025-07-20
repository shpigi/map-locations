# Publishing to PyPI

This guide explains how to publish the `map-locations` package to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account** (free):
   - Go to https://pypi.org/account/register/
   - Create an account with your email

2. **Test PyPI Account** (recommended):
   - Go to https://test.pypi.org/account/register/
   - Create a separate account for testing

3. **API Tokens**:
   - In your PyPI account: Account Settings → API tokens
   - Create a token with "Entire account" scope
   - Save the token securely

4. **Install publishing tools**:
   ```bash
   pip install twine
   ```

## Publishing Steps

### 1. Test PyPI (Recommended First Step)

```bash
# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ map-locations
```

### 2. Production PyPI

```bash
# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Install from PyPI
pip install map-locations
```

### 3. Using the Publish Script

```bash
# Publish to Test PyPI
./scripts/publish.sh test

# Publish to Production PyPI
./scripts/publish.sh prod
```

## Package Information

- **Package Name**: `map-locations`
- **PyPI URL**: https://pypi.org/project/map-locations/
- **Install Command**: `pip install map-locations`
- **CLI Command**: `map-locations --help`

## Version Management

To update the package version:

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # or whatever new version
   ```

2. Update version in `map_locations/__init__.py`:
   ```python
   __version__ = "0.1.1"
   ```

3. Build and publish:
   ```bash
   python -m build
   twine upload dist/*
   ```

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   - Make sure you have valid API tokens
   - Check your username and password

2. **Package Already Exists**:
   - You can't overwrite existing versions
   - Increment the version number

3. **Build Errors**:
   - Run `make clean` first
   - Check that all dependencies are installed

### Getting Help

- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- Twine Documentation: https://twine.readthedocs.io/

## Security Notes

- Never commit API tokens to version control
- Use environment variables or keyring for authentication
- Consider using GitHub Actions for automated publishing
