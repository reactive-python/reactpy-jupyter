To release a new version of idom-client-jupyter on PyPI:

- Update `_version.py` (set release version, remove 'dev')
- git add the `_version.py` file and git commit
- ```
  python setup.py sdist bdist_wheel
  twine upload dist/*
  git tag -a X.X.X -m 'comment'
  git add and git commit
  git push
  git push --tags
  ```

To release a new version of idom-client-jupyter on NPM:

- Update `js/package.json` with new npm package version
- ```
  # clean out the `dist` and `node_modules` directories
  git clean -fdx
  npm install
  npm publish
  ```
