import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    testTimeout: 10000,
    hookTimeout: 10000,
    pool: {
      forks: {
        singleFork: true
      }
    },
    sequence: {
      shuffle: false
    },
    maxConcurrency: 1
  },
});