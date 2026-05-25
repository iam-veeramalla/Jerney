const express = require('express');
const router = express.Router();
const { pool } = require('../db');

// GET all posts (newest first)
router.get('/', async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT p.*, 
        (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) as comment_count
       FROM posts p 
       ORDER BY p.created_at DESC`
    );
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch posts' });
  }
});

// GET single post with comments
router.get('/:id', async (req, res) => {
  try {
    const postResult = await pool.query('SELECT * FROM posts WHERE id = $1', [req.params.id]);
    if (postResult.rows.length === 0) {
      return res.status(404).json({ error: 'Post not found' });
    }

    const commentsResult = await pool.query(
      'SELECT * FROM comments WHERE post_id = $1 ORDER BY created_at DESC',
      [req.params.id]
    );

    res.json({
      ...postResult.rows[0],
      comments: commentsResult.rows,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch post' });
  }
});

// CREATE post
router.post('/', async (req, res) => {
  const { title, content, author, emoji } = req.body;

  if (!title || !content) {
    return res.status(400).json({ error: 'Title and content are required' });
  }

  try {
    const result = await pool.query(
      `INSERT INTO posts (title, content, author, emoji) 
       VALUES ($1, $2, $3, $4) 
       RETURNING *`,
      [title, content, author || 'Anonymous', emoji || '✨']
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to create post' });
  }
});

// UPDATE post
router.put('/:id', async (req, res) => {
  const { title, content, author, emoji } = req.body;

  if (!title || !content) {
    return res.status(400).json({ error: 'Title and content are required' });
  }

  try {
    const result = await pool.query(
      `UPDATE posts 
       SET title = $1, content = $2, author = $3, emoji = $4, updated_at = NOW() 
       WHERE id = $5 
       RETURNING *`,
      [title, content, author || 'Anonymous', emoji || '✨', req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Post not found' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to update post' });
  }
});

// DELETE post
router.delete('/:id', async (req, res) => {
  try {
    const result = await pool.query('DELETE FROM posts WHERE id = $1 RETURNING *', [req.params.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Post not found' });
    }
    res.json({ message: 'Post deleted successfully 🗑️' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to delete post' });
  }
});

module.exports = router;
