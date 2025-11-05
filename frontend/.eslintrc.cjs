module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
  rules: {
    'react/prop-types': 'off',
    'no-restricted-syntax': [
      'error',
      {
        selector: "JSXAttribute[name.name='className'][value.type='Literal'][value.value=/bg-facebook-/]",
        message: 'Use theme tokens (bg-surface/bg-neutral) instead of legacy bg-facebook-* classes.',
      },
      {
        selector: "JSXAttribute[name.name='className'][value.type='Literal'][value.value=/text-facebook-/]",
        message: 'Use theme tokens (text-primary/text-secondary) instead of text-facebook-* classes.',
      },
    ],
  },
};
