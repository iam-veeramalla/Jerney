import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getPost, updatePost } from '../api';
import { HiArrowLeft } from 'react-icons/hi2';
import toast from 'react-hot-toast';

const EMOJIS = ['✨', '🔥', '💡', '🚀', '💀', '🎯', '💎', '🌈', '🎵', '📸', '🧠', '💬', '❤️', '⚡', '🌊', '🍕'];

function EditPost() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [author, setAuthor] = useState('');
  const [emoji, setEmoji] = useState('✨');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPost();
  }, [id]);

  const fetchPost = async () => {
    try {
      const res = await getPost(id);
      setTitle(res.data.title);
      setContent(res.data.content);
      setAuthor(res.data.author);
      setEmoji(res.data.emoji || '✨');
    } catch (err) {
      toast.error('Post not found 😢');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title.trim() || !content.trim()) {
      toast.error('Title and content are required! 😤');
      return;
    }

    setSubmitting(true);
    try {
      await updatePost(id, {
        title: title.trim(),
        content: content.trim(),
        author: author.trim() || 'Anonymous',
        emoji,
      });
      toast.success('Post updated! Glow up complete ✨');
      navigate(`/post/${id}`);
    } catch (err) {
      toast.error('Failed to update post 😢');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <div className="form-page">
      <Link to={`/post/${id}`} className="post-detail-back">
        <HiArrowLeft size={16} /> Back to post
      </Link>
      <h1>Edit Post ✏️</h1>

      <form className="form-card" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Pick a vibe</label>
          <div className="emoji-picker">
            {EMOJIS.map((e) => (
              <button
                key={e}
                type="button"
                className={`emoji-option ${emoji === e ? 'selected' : ''}`}
                onClick={() => setEmoji(e)}
              >
                {e}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            id="title"
            type="text"
            placeholder="Something fire goes here..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={255}
          />
        </div>

        <div className="form-group">
          <label htmlFor="author">Author</label>
          <input
            id="author"
            type="text"
            placeholder="Your name"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            maxLength={100}
          />
        </div>

        <div className="form-group">
          <label htmlFor="content">Content</label>
          <textarea
            id="content"
            placeholder="Update your thoughts..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Saving...' : 'Save changes 💾'}
          </button>
          <Link to={`/post/${id}`} className="btn btn-secondary">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}

export default EditPost;
