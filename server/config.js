import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables from .env file
dotenv.config({ path: join(__dirname, '..', '.env') });

export const config = {
  db: {
    url: process.env.DATABASE_URL,
    pool: {
      max: 3,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 5000,
    },
    retry: {
      maxAttempts: 5,
      initialDelayMs: 1000,
    },
  },
  server: {
    port: parseInt(process.env.PORT || '3001', 10),
    env: process.env.NODE_ENV || 'development',
  },
};