import tseslint from 'typescript-eslint';
import hooks from 'eslint-plugin-react-hooks';
export default tseslint.config({ignores:['node_modules/**','dist/**','dist-module/**','.venv/**','.venv-deploy/**','deploy/hf-space*/**']},...tseslint.configs.recommended,{files:['**/*.ts','**/*.tsx'],plugins:{'react-hooks':hooks},rules:{...hooks.configs.recommended.rules,'@typescript-eslint/no-explicit-any':'off','@typescript-eslint/no-unused-vars':['error',{argsIgnorePattern:'^_',varsIgnorePattern:'^_'}]}});

