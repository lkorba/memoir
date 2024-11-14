import express from 'express';
import cors from 'cors';
import { config } from './config.js';
import db from './db.js';

const app = express();

app.use(cors());
app.use(express.json());

// Initialize database and start server
async function startServer() {
  try {
    // Connect to database with retries
    await db.connect();
    
    // Initialize database schema
    await db.initDb();
    
    // API Routes
    app.get('/api/entries', async (req, res) => {
      try {
        const result = await db.query(
          'SELECT id, title, content, created_at FROM entries ORDER BY created_at DESC'
        );
        res.json(result.rows);
      } catch (error) {
        console.error('Error fetching entries:', error);
        res.status(500).json({ error: 'Failed to fetch entries' });
      }
    });

    app.post('/api/entries', async (req, res) => {
      const { title, content } = req.body;
      if (!title || !content) {
        return res.status(400).json({ error: 'Title and content are required' });
      }

      try {
        const result = await db.query(
          'INSERT INTO entries (title, content) VALUES ($1, $2) RETURNING *',
          [title, content]
        );
        res.status(201).json(result.rows[0]);
      } catch (error) {
        console.error('Error creating entry:', error);
        res.status(500).json({ error: 'Failed to create entry' });
      }
    });

    app.get('/api/entries/:id', async (req, res) => {
      try {
        const result = await db.query(
          'SELECT id, title, content, created_at FROM entries WHERE id = $1',
          [req.params.id]
        );
        
        if (result.rows.length === 0) {
          return res.status(404).json({ error: 'Entry not found' });
        }
        
        res.json(result.rows[0]);
      } catch (error) {
        console.error('Error fetching entry:', error);
        res.status(500).json({ error: 'Failed to fetch entry' });
      }
    });

    app.put('/api/entries/:id', async (req, res) => {
      const { title, content } = req.body;
      if (!title || !content) {
        return res.status(400).json({ error: 'Title and content are required' });
      }

      try {
        const result = await db.query(
          'UPDATE entries SET title = $1, content = $2 WHERE id = $3 RETURNING *',
          [title, content, req.params.id]
        );
        
        if (result.rows.length === 0) {
          return res.status(404).json({ error: 'Entry not found' });
        }
        
        res.json(result.rows[0]);
      } catch (error) {
        console.error('Error updating entry:', error);
        res.status(500).json({ error: 'Failed to update entry' });
      }
    });

    app.delete('/api/entries/:id', async (req, res) => {
      try {
        const result = await db.query(
          'DELETE FROM entries WHERE id = $1 RETURNING *',
          [req.params.id]
        );
        
        if (result.rows.length === 0) {
          return res.status(404).json({ error: 'Entry not found' });
        }
        
        res.json({ message: 'Entry deleted successfully' });
      } catch (error) {
        console.error('Error deleting entry:', error);
        res.status(500).json({ error: 'Failed to delete entry' });
      }
    });

    // Start server
    const server = app.listen(config.server.port, () => {
      console.log(`Server running on port ${config.server.port}`);
    });

    // Graceful shutdown
    const shutdown = async () => {
      console.log('Shutting down gracefully...');
      server.close(async () => {
        console.log('HTTP server closed');
        await db.close();
        process.exit(0);
      });
    };

    process.on('SIGTERM', shutdown);
    process.on('SIGINT', shutdown);

  } catch (error) {
    console.error('Failed to start server:', error);
    await db.close();
    process.exit(1);
  }
}

startServer();