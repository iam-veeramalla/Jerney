const express = require('express');
const router = express.Router();
const { pool } = require('../db');

// GET comments for a post
router.get('/post/:postId', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM comments WHERE post_id = $1 ORDER BY created_at DESC',
      [req.params.postId]
    );
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch comments' });
  }
});

// CREATE comment
router.post('/', async (req, res) => {
  const { post_id, author, content } = req.body;

  if (!post_id || !content) {
    return res.status(400).json({ error: 'Post ID and content are required' });
  }

  try {
    // Verify post exists
    const postCheck = await pool.query('SELECT id FROM posts WHERE id = $1', [post_id]);
    if (postCheck.rows.length === 0) {
      return res.status(404).json({ error: 'Post not found' });
    }

    const result = await pool.query(
      'INSERT INTO comments (post_id, author, content) VALUES ($1, $2, $3) RETURNING *',
      [post_id, author || 'Anonymous', content]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to create comment' });
  }
});

// DELETE comment
router.delete('/:id', async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM comments WHERE id = $1 RETURNING *', [req.params.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Comment not found' });
    }
    res.json({ message: 'Comment deleted 🗑️' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to delete comment' });
  }
});

module.exports = router;
