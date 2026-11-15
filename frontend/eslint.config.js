// https://docs.expo.dev/guides/using-eslint/
const { defineConfig } = require('eslint/config');
const expoConfig = require('eslint-config-expo/flat');

module.exports = defineConfig([
  expoConfig,
  {
    // esquema.ts lo genera openapi-typescript y __fixtures__ el script fixtures:copiar.
    ignores: ['dist/*', 'src/shared/api/esquema.ts', 'src/shared/api/__fixtures__/*'],
  },
  {
    files: ['**/__tests__/**', 'jest.setup.js'],
    languageOptions: { globals: { jest: 'readonly' } },
  },
]);
