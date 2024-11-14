import pg from 'pg';
import { config } from './config.js';

const { Pool } = pg;

class Database {
  constructor() {
    this._pool = null;
  }

  get pool() {
    if (!this._pool) {
      this._pool = new Pool({
        connectionString: config.db.url,
        ...config.db.pool,
        ssl: {
          rejectUnauthorized: false
        }
      });

      this._pool.on('error', (err) => {
        console.error('Unexpected error on idle client', err);
      });

      this._pool.on('connect', () => {
        console.log('New client connected to database');
      });
    }
    return this._pool;
  }

  async connect(retries = config.db.retry.maxAttempts) {
    let lastError;
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const client = await this.pool.connect();
        try {
          await client.query('SELECT 1');
          console.log('Database connection established');
          client.release();
          return true;
        } catch (err) {
          client.release();
          throw err;
        }
      } catch (err) {
        lastError = err;
        console.error(`Connection attempt ${attempt} failed:`, err.message);
        if (attempt < retries) {
          const delay = config.db.retry.initialDelayMs * Math.pow(2, attempt - 1);
          console.log(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    throw new Error(`Failed to connect after ${retries} attempts: ${lastError?.message}`);
  }

  async query(text, params) {
    const client = await this.pool.connect();
    try {
      const start = Date.now();
      const result = await client.query(text, params);
      const duration = Date.now() - start;
      console.log('Executed query', { text, duration, rows: result.rowCount });
      return result;
    } finally {
      client.release();
    }
  }

  async initDb() {
    try {
      await this.query(`
        CREATE TABLE IF NOT EXISTS entries (
          id SERIAL PRIMARY KEY,
          title VARCHAR(255) NOT NULL,
          content TEXT NOT NULL,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
      `);
      console.log('Database schema initialized successfully');
    } catch (err) {
      console.error('Failed to initialize database schema:', err);
      throw err;
    }
  }

  async close() {
    if (this._pool) {
      await this._pool.end();
      this._pool = null;
      console.log('Database connection pool closed');
    }
  }
}

// Export singleton instance
const db = new Database();
export default db;