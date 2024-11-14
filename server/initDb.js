import { initDb, closePool } from './db.js';

async function initialize() {
  try {
    await initDb();
    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Failed to initialize database:', error);
    process.exit(1);
  } finally {
    await closePool();
  }
}

initialize();