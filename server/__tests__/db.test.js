import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import db from '../db.js';

describe('Database Operations', () => {
  beforeAll(async () => {
    try {
      await db.connect();
      await db.initDb();
    } catch (error) {
      console.error('Test setup failed:', error);
      throw error;
    }
  });

  afterEach(async () => {
    try {
      await db.query('DELETE FROM entries WHERE title LIKE $1', ['Test Entry%']);
    } catch (error) {
      console.error('Cleanup failed:', error);
    }
  });

  afterAll(async () => {
    await db.close();
  });

  it('should connect to the database', async () => {
    const result = await db.query('SELECT NOW()');
    expect(result.rows).toBeDefined();
  });

  it('should create a new entry', async () => {
    const title = 'Test Entry 1';
    const content = 'Test Content 1';
    
    const result = await db.query(
      'INSERT INTO entries (title, content) VALUES ($1, $2) RETURNING *',
      [title, content]
    );

    expect(result.rows[0]).toEqual(
      expect.objectContaining({
        title,
        content,
      })
    );
  });

  it('should retrieve an entry', async () => {
    const title = 'Test Entry 2';
    const content = 'Test Content 2';
    
    const createResult = await db.query(
      'INSERT INTO entries (title, content) VALUES ($1, $2) RETURNING *',
      [title, content]
    );
    
    const id = createResult.rows[0].id;
    
    const result = await db.query(
      'SELECT * FROM entries WHERE id = $1',
      [id]
    );

    expect(result.rows[0]).toEqual(
      expect.objectContaining({
        id,
        title,
        content,
      })
    );
  });

  it('should handle errors gracefully', async () => {
    await expect(
      db.query('INSERT INTO entries (title) VALUES ($1)', ['Test Entry'])
    ).rejects.toThrow();

    await expect(
      db.query('SELECT invalid_column FROM entries')
    ).rejects.toThrow();
  });
});